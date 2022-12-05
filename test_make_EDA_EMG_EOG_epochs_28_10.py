import argparse
from joblib import Parallel, delayed
import pandas as pd

import mne
from mne_bids import BIDSPath
import autoreject 

from utils import prepare_dataset


# Prepare a name to save the data
# Prepare a name to save the data
subject = '30'
epo_fname_in = 'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_epo.fif'
  

epochs = mne.read_epochs(epo_fname_in, proj=False)

#%%

# Make epochs EDA
epochsEDA = epochs.copy().pick_channels(ch_names=['EDA_Phasic','EDA_Tonic', 'EDA_SMNA'])

#%%
epochsEDA_SMNA = epochs.copy().pick_channels(ch_names=['EDA_SMNA'])
# %%
epochsEDA_SMNA.get_data().squeeze().mean(axis=1).shape
#%%
import matplotlib.pyplot as plt
plt.plot(epochsEDA_SMNA.get_data().squeeze().mean(axis=1))

#%%