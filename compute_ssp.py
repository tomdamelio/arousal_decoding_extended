import argparse
from joblib import Parallel, delayed
import pandas as pd

import mne
from mne_bids import BIDSPath
import autoreject 

from utils import prepare_dataset

DATASETS = ['deap']
parser = argparse.ArgumentParser(description='Compute SSP.')
parser.add_argument(
    '-d', '--dataset',
    default=None,
    nargs='+',
    help='the dataset for which preprocessing should be computed')
parser.add_argument(
    '--n_jobs', type=int, default=-1,
    help='number of parallel processes to use (default: Max Jobs)')
args = parser.parse_args()
datasets = args.dataset
n_jobs = args.n_jobs
if datasets is None:
    datasets = list(DATASETS)
print(f"Datasets: {', '.join(datasets)}")

DEBUG = False

def _get_global_reject_ssp(raw, decim):
    if 'eog' in raw:
        eog_epochs = mne.preprocessing.create_eog_epochs(raw)
    else:
        eog_epochs = []
    if len(eog_epochs) >= 5:
        reject_eog = autoreject.get_rejection_threshold(eog_epochs, decim=decim)
        del reject_eog['eog']  # we don't want to reject eog based on eog
    else:
        reject_eog = None
        
    return reject_eog

def run_and_apply_ssp(subject, cfg):
    
    ok = 'OK'
    
    ### Run SSP ###
    bids_path = BIDSPath(subject=subject,
                         session=None,
                         task=cfg.task,
                         datatype=cfg.data_type,
                         extension='.fif',
                         root=cfg.deriv_root)

    # Prepare a name to save the data
    raw_fname_in = bids_path.copy().update(processing='filt', suffix='raw',
                                           check=False)
        
    raw = mne.io.read_raw_fif(raw_fname_in)
    
    reject_eog = _get_global_reject_ssp(
        raw, decim=5)
    
    if 'eog' in raw:
        eog_projs, events = mne.preprocessing.compute_proj_eog(
            raw, n_grad=0, n_mag=0, n_eeg=1, reject=reject_eog)

    ### Apply SSP ###
    
    # Prepare a name to save the data
    epo_fname_in = bids_path.copy().update(processing='clean', suffix='epo',
                                           check=False)
    
    epochs = mne.read_epochs(epo_fname_in, proj=False)
    
    epochs_cleaned = epochs.copy().pick_types(eeg = True).add_proj(eog_projs).apply_proj()
    
    epo_fname_out = epo_fname_in.copy().update(processing="SSP")
    
    epochs_cleaned.save(epo_fname_out, overwrite=True)
    return ok

for dataset in datasets:
    cfg, subjects = prepare_dataset(dataset)
    print(cfg.session)
    N_JOBS = (n_jobs if n_jobs else cfg.N_JOBS)

    if DEBUG:
        subjects = subjects[:1]
        N_JOBS = 1

    print(f"computing SSP on {dataset}")
    logging = Parallel(n_jobs=N_JOBS)(
        delayed(run_and_apply_ssp)(sub.split('-')[1], cfg) for sub in subjects)
