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
DEBUG = True

#%%

pathEDA = './outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-01/eeg/sub-01_task-rest_proc-EDA_epoRejected.fif'
epochs = mne.read_epochs(pathEDA, proj=False, preload=True)
epochs = epochs.copy().pick_channels(ch_names=['EDA'])

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
    return EDA_features # should be len(epochs) x (2) n_features (meanEDA and VarEDA)

#%%
pathEMG = './outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-01/eeg/sub-01_task-rest_proc-EMG_epoRejected.fif'
epochs = mne.read_epochs(pathEMG, proj=False, preload=True)
epochs = epochs.copy().pick_types(emg=True)

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

    return EMG_features # should be len(epochs) x (2) n_features (meanEMG and VarEMG)

#%%
pathEOG = './outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-01/eeg/sub-01_task-rest_proc-EOG_epoRejected.fif'
epochs = mne.read_epochs(pathEOG, proj=False, preload=True)
epochs = epochs.copy().pick_types(eog=True)

def extract_EOG_measures(epochs):
    # Input -> EpochsEDA
    # Output -> n_epochs x 2 features (meanEOG and varEOG)

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
    return EOG_features # # should be len(epochs) x (8) n_features (meanEOG and VarEOG)
# %%
