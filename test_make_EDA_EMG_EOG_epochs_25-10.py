#%%
import argparse
from joblib import Parallel, delayed
import pandas as pd

import mne
from mne_bids import BIDSPath
import autoreject 

from utils import prepare_dataset

#%%
# Prepare a name to save the data
subject = '29'
epo_fname_in = 'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-EDA_epoRejected.fif'
    
epochs = mne.read_epochs(epo_fname_in, proj=False)

#%%
EDA_mean = epochs.get_data().mean(axis=2)

# %%
import matplotlib.pyplot as plt
y = EDA_mean[:,2]
plt.plot(y)
# %%
