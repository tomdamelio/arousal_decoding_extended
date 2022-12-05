#%%epare_dataset
import argparse
from multiprocessing import Value

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

import mne
from mne_bids import BIDSPath

import h5io

from utils import prepare_dataset

subject = '32'
bp = 'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject  +'/eeg/sub-' + subject +'_task-rest_proc-EDA_epoRejected.fif'
#bp = 'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject  +'/eeg/sub-' + subject +'_task-rest_proc-autoreject_epo.fif'

#bp = 'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject  +'/eeg/sub-' + subject +'_task-rest_proc-filt_raw.fif'


#%%
#raw = mne.io.read_raw_fif(bp,
#                    preload=True)

#%%

#raw_eda_smna = raw.copy().pick_channels(ch_names=['EDA_SMNA'])

#raw_eda_np = raw_eda_smna.get_data()

#%%
#import matplotlib.pyplot as plt
#plt.plot(raw_eda_np[0])


#%%
# read epochs

epochs = mne.read_epochs(bp,
                        proj=False,
                        preload=True)

#%%

epochs_eda = epochs.copy().pick_channels(ch_names=['EDA_Phasic', 'EDA_Tonic', 'EDA_SMNA', 'EDA'])


#%%
%matplotlib
#epochs.plot(picks = 'EDA_Phasic')

#%%
EDA_mean = epochs.get_data().mean(axis=2) # keep 3 EDA means
EDA_var = epochs.get_data().var(axis=2) # keep 3 EDA vars
EDA_features_ndarray = np.hstack((EDA_mean,EDA_var))
df_EDA_features = pd.DataFrame(EDA_features_ndarray, columns = ['meanEDA_Phasic', 'meanEDA_Tonic',
                                'meanEDA_SMNA', 'varEDA_Phasic',
                                'varEDA_Tonic', 'varEDA_SMNA'])
EDA_features = df_EDA_features.to_dict(orient = 'list')
for key, value in EDA_features.items():
    EDA_features[key] = np.array(value)

#%%
# Plot EDA_features['meanEDA_SMNA']
import matplotlib.pyplot as plt
plt.plot(EDA_features['meanEDA_Phasic'])

#%%
#import matplotlib.pyplot as plt
epochs_SMNA = epochs.copy().pick_channels(ch_names=['EDA_SMNA'])
epochs_SMNA_np = epochs_SMNA.get_data().mean(axis=2)
plt.plot(epochs_SMNA_np)
# %%
len(epochs_SMNA_np)

#%%