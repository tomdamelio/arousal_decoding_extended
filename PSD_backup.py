#%%
import mne
import os.path as op
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import datetime
import importlib
import os
import os.path as op

import h5io

plt.rcParams['figure.figsize'] = [20, 8] 

dataset =  'deap'
config_map = {'deap': "config_deap_eeg"}

cfg = importlib.import_module(config_map[dataset])
bids_root = cfg.bids_root
deriv_root = cfg.deriv_root
analyze_channels = cfg.analyze_channels

condition = 'rest'
feature_label = 'fb_covs'

#########  SET CONFIGS #########

# eda or emg?    
measure = 'eda'
# var or mean?   
y_stat = 'var'

DEBUG = True

################################


derivative_path = deriv_root 
pred_path = derivative_path / f'{measure}_predictions'

#%%


date = datetime.datetime.now().strftime("%d-%m--%H-%M")    
n_components = np.arange(1, 32, 1)
seed = 42
n_splits = 5
n_jobs = -1
score_name, scoring = "r2", "r2"
cv_name = '5Fold'


features_y = h5io.read_hdf5(deriv_root / f'features_EDA_{condition}.h5')

#subjects = ['sub-01']

#subjects = ['sub-01', 'sub-02', 'sub-03', 'sub-04', 'sub-05', 'sub-06', 'sub-07', 'sub-08',
#            'sub-09', 'sub-10', 'sub-11', 'sub-12', 'sub-13', 'sub-14', 'sub-15', 'sub-16',
#            'sub-17', 'sub-18', 'sub-19', 'sub-20', 'sub-21', 'sub-22', 'sub-23', 'sub-24',
#            'sub-25', 'sub-26', 'sub-27', 'sub-28', 'sub-29', 'sub-30', 'sub-31', 'sub-32']

subjects = ['sub-01', 'sub-02']

#%%

for subject in subjects:
        
        eda_features = [features_y[subject]]
        y = eda_features[0]['meanEDA_SMNA']
        
        idx_low_EDA_aux = []
        idx_high_EDA_aux = []
        for ii in range(len(y)-1):
            if y[ii] < np.percentile(y, 25):
                idx_low_EDA_aux.append(ii)
            elif y[ii] > np.percentile(y, 75):
                idx_high_EDA_aux.append(ii)
             
        number_subject = subject[-2:]
        
        
        extension = '.fif'
        directory = 'outputs/DEAP-bids/derivatives/mne-bids-pipeline/'
        fname_fif = op.join(directory, 'sub-' + number_subject , 'eeg',
                      'sub-' + number_subject + '_task-rest_epo' + extension)
        epochs_aux = mne.read_epochs(fname_fif, preload=True)
        
        try:
            idx_low_EDA_aux = [i + len(epochs) for i in idx_low_EDA_aux]
            idx_low_EDA.append(idx_low_EDA_aux)
        except Exception:
            pass
        
        try:
            idx_high_EDA_aux = [i + len(epochs) for i in idx_high_EDA_aux]
            idx_high_EDA.append(idx_high_EDA_aux)
        except Exception:
            pass
        
        try:
            epochs_now = epochs.copy()
            epochs = mne.concatenate_epochs([epochs_now, epochs_aux])
        except Exception:
            epochs = epochs_aux.copy()
            idx_low_EDA = idx_low_EDA_aux
            idx_high_EDA = idx_high_EDA_aux
        

from collections import Iterable
def flatten(lis):
     for item in lis:
         if isinstance(item, Iterable) and not isinstance(item, str):
             for x in flatten(item):
                 yield x
         else:        
             yield item

idx_low_EDA = list(flatten(idx_low_EDA))
idx_high_EDA = list(flatten(idx_high_EDA))


f, ax = plt.subplots()

psds, freqs = mne.time_frequency.psd_multitaper(epochs[idx_low_EDA], fmin=0, fmax=80, n_jobs=1)
psds = 10 * np.log10(psds)  # convert to dB
psds_mean = psds.mean(0).mean(0)
psds_std = psds.mean(0).std(0)

ax.plot(freqs, psds_mean, color='g', label='Low EDA')
ax.fill_between(freqs, psds_mean - psds_std, psds_mean + psds_std,
              color='g', alpha=.3)

psds, freqs = mne.time_frequency.psd_multitaper(epochs[idx_high_EDA], fmin=0, fmax=80, n_jobs=1)
psds = 10 * np.log10(psds)  # convert to dB
psds_mean = psds.mean(0).mean(0)
psds_std = psds.mean(0).std(0)

ax.plot(freqs, psds_mean, color='r', label='High EDA')
ax.fill_between(freqs, psds_mean - psds_std, psds_mean + psds_std,
              color='r', alpha=.3)

ax.legend()

