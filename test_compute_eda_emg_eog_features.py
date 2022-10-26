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
# Test read data output
# Pruebo abrir cov matrices de mi tesis
import h5io
import numpy as np
import pandas as pd
import importlib

dataset =  'deap'
config_map = {'deap': "config_deap_eeg"}


cfg = importlib.import_module(config_map[dataset])
bids_root = cfg.bids_root
deriv_root = cfg.deriv_root
analyze_channels = cfg.analyze_channels

condition = 'rest'
FEATURE_TYPE = 'EDA'

df_subjects = pd.read_csv(bids_root / "participants.tsv", sep='\t')
df_subjects = df_subjects.set_index('participant_id')
df_subjects = df_subjects.sort_index()  

features = h5io.read_hdf5(
    deriv_root / f'features_{FEATURE_TYPE}_{condition}.h5')

eda_features = list()
subjects = df_subjects.index.values
subjects = subjects.tolist()


DEBUG = True
if DEBUG:
    subjects = ['sub-01','sub-02','sub-03']
    
dict_features = {}    

for sub in subjects:
    eda_features = [features[sub]]
    X_eda_features= np.array([cc for cc in eda_features])
    X_eda_features = np.squeeze(X_eda_features, axis=0)  
    #if DEBUG:
    #    X_eda_features = X_eda_features[:30,:,:,:]
    dict_features[sub] = X_eda_features  
    
# %%
#Open data and inspect new channels (created after `add_annotations`. This has to be in `epoched EDA`)
import numpy as np
import pandas as pd
import mne
pathEDA = './outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-03/eeg/sub-03_task-rest_proc-EDA_epoRejected.fif'
epochs = mne.read_epochs(pathEDA, proj=False, preload=True)
epochs.info


#%%
# Open filter data file and see if there are alls peripheral singals there
import numpy as np
import pandas as pd
import mne
#pathEDA = './outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-03/eeg/sub-03_task-rest_proc-clean_epo.fif'
pathEDA = './outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-03/eeg/sub-03_task-rest_proc-EDA_epo.fif'
epochs = mne.read_epochs(pathEDA, proj=False, preload=True)
epochs.info

#%%
# test compute_eda_features




#%%
epochs = epochs.copy().pick_channels(ch_names=['EDA_Phasic','EDA_Tonic'])


