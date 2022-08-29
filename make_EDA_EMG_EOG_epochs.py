import argparse
from joblib import Parallel, delayed
import pandas as pd

import mne
from mne_bids import BIDSPath
import autoreject 

from utils import prepare_dataset

DATASETS = ['deap']
parser = argparse.ArgumentParser(description='Make EDA and EMG epochs.')
parser.add_argument(
    '-d', '--dataset',
    default=None,
    nargs='+',
    help='the dataset for which preprocessing should be computed')
parser.add_argument(
    '--n_jobs', type=int, default=1,
    help='number of parallel processes to use')
args = parser.parse_args()
datasets = args.dataset
n_jobs = args.n_jobs
if datasets is None:
    datasets = list(DATASETS)
print(f"Datasets: {', '.join(datasets)}")

DEBUG = False

def make_EDA_EMG_and_EOG_epochs(subject, cfg):
    
    ok = 'OK'
    
    ### Make Epochs EDA, EMG and EOG epochs ###
    bids_path = BIDSPath(subject=subject,
                         session=None,
                         task=cfg.task,
                         datatype=cfg.data_type,
                         extension='.fif',
                         root=cfg.deriv_root)

    # Prepare a name to save the data
    epo_fname_in = bids_path.copy().update(processing='clean',
                                            suffix='epo',
                                            check=False)
        
    epochs = mne.read_epochs(epo_fname_in, proj=False)
    
    # Make epochs EDA
    epochsEDA = epochs.copy().pick_channels(ch_names=['EDA'])
    epo_fname_out_EDA = epo_fname_in.copy().update(processing="EDA")
    epochsEDA.save(epo_fname_out_EDA, overwrite=True)
    
    # Make epochs EMG
    epochsEMG = epochs.copy().pick_types(emg=True)
    epo_fname_out_EMG = epo_fname_in.copy().update(processing="EMG")
    epochsEMG.save(epo_fname_out_EMG, overwrite=True)
    
    # Make epochs EOG
    epochsEOG = epochs.copy().pick_types(eog=True)
    epo_fname_out_EOG = epo_fname_in.copy().update(processing="EOG")
    epochsEOG.save(epo_fname_out_EOG, overwrite=True)
    
    return ok

for dataset in datasets:
    cfg, subjects = prepare_dataset(dataset)
    print(cfg.session)
    N_JOBS = (n_jobs if n_jobs else cfg.N_JOBS)

    if DEBUG:
        subjects = subjects[:1]
        N_JOBS = 1

    print(f"Computing EDA, EMG and EOG epochs on {dataset}")
    logging = Parallel(n_jobs=N_JOBS)(
        delayed(make_EDA_EMG_and_EOG_epochs)(sub.split('-')[1], cfg) for sub in subjects)
