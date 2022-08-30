#%%
import argparse
from multiprocessing import Value

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

import mne
from mne_bids import BIDSPath
import coffeine
import h5io

from utils import prepare_dataset

DATASETS = ['deap']
FEATURE_TYPE = ['EDA', 'EMG', 'EOG']
parser = argparse.ArgumentParser(description='Compute features EDA EMG EOG.')
parser.add_argument(
    '-d', '--dataset',
    default=None,
    nargs='+',
    help='the dataset for which features should be computed')
parser.add_argument(
    '-t', '--feature_type',
    default=None,
    nargs='+', help='Type of features to compute')
parser.add_argument(
    '--n_jobs', type=int, default=4,
    help='number of parallel processes to use (default: 4)')

args = parser.parse_args()
datasets = args.dataset
feature_types = args.feature_type
n_jobs = args.n_jobs
if datasets is None:
    datasets = list(DATASETS)
if feature_types is None:
    feature_types = list(FEATURE_TYPE)
tasks = [(ds, bs) for ds in datasets for bs in feature_types]
for dataset, feature_type in tasks:
    if dataset not in DATASETS:
        raise ValueError(f"The dataset '{dataset}' passed is unkonwn")
    if feature_type not in FEATURE_TYPE:
        raise ValueError(f"The benchmark '{feature_type}' passed is unkonwn")
print(f"Running benchmarks: {', '.join(feature_types)}")
print(f"Datasets: {', '.join(datasets)}")

#%%

DEBUG = True

def extract_EDA_measures(epochs):
    # Input -> EpochsEDA
    # Output -> n_epochs x 2 features (meanEDA and varEDA)
    EDA_features = {}
    if DEBUG:
        epochs = epochs[:30]
    EDA_mean = epochs.get_data().mean(axis=2)[:, 0]
    EDA_var = epochs.get_data().var(axis=2)[:, 0]  
    EDA_features['mean'] = EDA_mean
    EDA_features['var'] = EDA_var
    return EDA_features 

def extract_EMG_measures(epochs):
    # Input -> EpochsEMG
    # Output -> n_epochs x 2 features (meanEMG and varEMG)
    epochs = epochs.copy().pick_channels(['EXG5','EXG6'])
    EMG_features = {}
    if DEBUG:
        epochs = epochs[:30]

    # EMG activity = EMG z1 - EMG z2
    emg = epochs.get_data()
    emgz1 = emg[:,0,:]
    emgz2 = emg[:,1,:]
    
    emg_delta = emgz1 - emgz2
    
    EMG_features['mean']  = emg_delta.mean(axis=1)
    EMG_features['var'] = emg_delta.var(axis=1)        

    return EMG_features 

def extract_EOG_measures(epochs):
    # Input -> EpochsEOG
    # Output -> n_epochs x 8 features (meanEOG and varEOG)

    if DEBUG:
        epochs = epochs[:30]
    EOG_mean = epochs.get_data().mean(axis=2) # keep 4 EOG means
    EOG_var = epochs.get_data().var(axis=2) # keep 4 EOG vars
    EOG_features_ndarray = np.hstack((EOG_mean,EOG_var))
    df_EOG_features = pd.DataFrame(EOG_features_ndarray, columns = ['meanEOG1', 'meanEOG2',
                                    'meanEOG3', 'meanEOG4',
                                    'varEOG1', 'varEOG2',
                                    'varEOG3', 'varEOG4'])
    EOG_features = df_EOG_features.to_dict(orient = 'list')
    for key, value in EOG_features.items():
        EOG_features[key] = np.array(value)
    return EOG_features 


def run_subject(subject, cfg, condition):
    task = cfg.task
    deriv_root = cfg.deriv_root
    data_type = cfg.data_type
    session = cfg.session
    if session.startswith('ses-'):
        session = session.lstrip('ses-')

    bp_args = dict(root=deriv_root, subject=subject,
                    datatype=data_type, processing=feature_type,
                    task=task,
                    check=False, suffix="epoRejected")
    if session:
        bp_args['session'] = session
    bp = BIDSPath(**bp_args)

    if not bp.fpath.exists():
        return 'no file'

    epochs = mne.read_epochs(bp, proj=False, preload=True)
    if not any(condition in cc for cc in epochs.event_id):
        return 'condition not found'
    out = None
    # make sure that no EOG/ECG made it into the selection
    
    try:
        if feature_type == 'EDA':       
            epochs = epochs.copy().pick_channels(ch_names=['EDA'])
            out = extract_EDA_measures(epochs)
        elif feature_type == 'EMG':
            epochs = epochs.copy().pick_types(emg=True)
            out = extract_EMG_measures(epochs)
        elif feature_type == 'EOG':
            epochs = epochs.copy().pick_types(eog=True)
            out = extract_EOG_measures(epochs)
        else:
            NotImplementedError()
    except Exception as err:
        raise err
        return repr(err)

    return out


for dataset, feature_type in tasks:
    cfg, subjects = prepare_dataset(dataset)
    N_JOBS = cfg.N_JOBS if not n_jobs else n_jobs
    if DEBUG:
        subjects = subjects[:3]
        N_JOBS = 4
        #frequency_bands = {"alpha": (8.0, 14.0)}

    for condition in cfg.feature_conditions:
        print(
            f"Computing {feature_type} features on {dataset} for '{condition}'")
        features = Parallel(n_jobs=N_JOBS)(
            delayed(run_subject)(sub.split('-')[1], cfg=cfg,
            condition=condition) for sub in subjects)

        out = {sub: ff for sub, ff in zip(subjects, features)
                if not isinstance(ff, str)}

        label = 'rest'

        out_fname = cfg.deriv_root / f'features_{feature_type}_{label}.h5'
        log_out_fname = (
            cfg.deriv_root / f'feature_{feature_type}_{label}-log.csv')

        h5io.write_hdf5(
            out_fname,
            out,
            overwrite=True
        )
        print(f'Features saved under {out_fname}.')

        logging = ['OK' if not isinstance(ff, str) else ff for sub, ff in
                    zip(subjects, features)]
        out_log = pd.DataFrame({"ok": logging, "subject": subjects})
        out_log.to_csv(log_out_fname)
        print(f'Log saved under {log_out_fname}.')