'''
- INPUT: 
    - Epocas de EDA
    - Epocas de EMG
    - Epocas de EOG
    - Numpy array de epocas rejecteadas

- OUTPUT: 
    - Epocas de EDA autorejecteadas
    - Epocas de EMG autorejecteadas
    - Epocas de EOG autorejecteadas
'''
import argparse
from joblib import Parallel, delayed
import pandas as pd
from numpy import load

import mne
from mne_bids import BIDSPath
import autoreject 

from utils import prepare_dataset

DATASETS = ['deap']
parser = argparse.ArgumentParser(description='Reject autorejeted Epochs in EDA EMG and EOG.')
parser.add_argument(
    '-d', '--dataset',
    default=None,
    nargs='+',
    help='the dataset for which preprocessing should be computed')
parser.add_argument(
    '--n_jobs', type=int, default=-1,
    help='number of parallel processes to use (Default = -1)')
args = parser.parse_args()
datasets = args.dataset
n_jobs = args.n_jobs
if datasets is None:
    datasets = list(DATASETS)
print(f"Datasets: {', '.join(datasets)}")

DEBUG = False

def reject_epochs(subject, cfg):
    
    ok = 'OK'
    
    bids_path = BIDSPath(subject=subject,
                        session=None,
                        task=cfg.task,
                        datatype=cfg.data_type,
                        extension='.fif',
                        root=cfg.deriv_root)

    # Load EDA epochs
    epochsEDA_fname = bids_path.copy().update(processing='EDA',
                                                suffix='epo',
                                                check=False)

    epochsEDA = mne.read_epochs(epochsEDA_fname, proj=False)

    # Load EMG epochs
    epochsEMG_fname = bids_path.copy().update(processing='EMG',
                                                suffix='epo',
                                                check=False)  
    epochsEMG = mne.read_epochs(epochsEMG_fname, proj=False)

    # Load EOG epochs
    epochsEOG_fname = bids_path.copy().update(processing='EOG',
                                                suffix='epo',
                                                check=False)   
    epochsEOG = mne.read_epochs(epochsEOG_fname, proj=False)

    # Load numpy array with autorejected epochs
    reject_log_data = load('./outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-logsAutoreject_epo.npz')
    reject_log = autoreject.autoreject.RejectLog(bad_epochs=reject_log_data['bad_epochs'],
                                                labels=reject_log_data['labels'],
                                                ch_names=reject_log_data['ch_names'])
    bad_epochs = reject_log.bad_epochs
    bad_epochs_inv = []
    for annot in range(len(bad_epochs-1)):
        if bad_epochs[annot] == True:
            bad_epochs_inv.append(False)
        elif bad_epochs[annot] == False:
            bad_epochs_inv.append(True)

    # Reject autorejected epochs in EDA, EMG and EOG
    epochsEDA = epochsEDA[bad_epochs_inv]
    epochsEMG = epochsEMG[bad_epochs_inv]
    epochsEOG = epochsEOG[bad_epochs_inv]
    
    # Save EDA, EMG and EOG epochs after rejection
    epochsEDA_fname_autoreject = epochsEDA_fname.copy().update(processing='EDA',
                                                                suffix='epoRejected',
                                                                check=False) 
    epochsEDA.save(epochsEDA_fname_autoreject, overwrite=True)
    
    epochsEMG_fname_autoreject = epochsEMG_fname.copy().update(processing='EMG',  
                                                                suffix='epoRejected',
                                                                check=False) 
    epochsEMG.save(epochsEMG_fname_autoreject, overwrite=True)
    
    epochsEOG_fname_autoreject = epochsEOG_fname.copy().update(processing='EOG',  
                                                                suffix='epoRejected',
                                                                check=False) 
    epochsEOG.save(epochsEOG_fname_autoreject, overwrite=True)
    
    return ok

for dataset in datasets:
    cfg, subjects = prepare_dataset(dataset)
    print(cfg.session)
    N_JOBS = (n_jobs if n_jobs else cfg.N_JOBS)

    if DEBUG:
        subjects = subjects[22:]
        N_JOBS = 3

    print(f"Reject autorejeted Epochs in EDA EMG and EOG on {dataset}")
    logging = Parallel(n_jobs=N_JOBS)(
        delayed(reject_epochs)(sub.split('-')[1], cfg) for sub in subjects)
