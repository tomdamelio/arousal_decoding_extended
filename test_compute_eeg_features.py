#%%

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
feature_label = 'fb_covs'

frequency_bands = {
    "delta": (0.1, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 14.0),
    "beta": (14.0, 30.0),
    "gamma": (30.0, 80.0),
}

df_subjects = pd.read_csv(bids_root / "participants.tsv", sep='\t')
df_subjects = df_subjects.set_index('participant_id')
df_subjects = df_subjects.sort_index()  

features = h5io.read_hdf5(
    deriv_root / f'features_{feature_label}_{condition}.h5')

covs = list()
subjects = df_subjects.index.values
subjects = subjects.tolist()


DEBUG = False
if DEBUG:
    subjects = ['sub-01','sub-02','sub-03']
    
dict_features = {}    

for sub in subjects:
    covs = [features[sub]]
    X_cov = np.array([cc for cc in covs])
    X_cov = np.squeeze(X_cov, axis=0)  
    if DEBUG:
        X_cov = X_cov[:30,:,:,:]
    dict_features[sub] = X_cov  

#%%        
#df_features = pd.DataFrame.from_dict(pd.DataFrame(
#        {band: list(dict_features['sub-01'][:, ii]) for ii, band in
#        enumerate(frequency_bands)}))
#
##%%    
#    df_features = pd.DataFrame(
#        {band: list(X_cov[:, ii]) for ii, band in
#        enumerate(frequency_bands)})
## %%
## Pruebo abrir cov matrices de mi tesis
#import mne
#import h5io
#covs_viejo = h5io.read_hdf5('C:/Users/dadam/OneDrive/Escritorio/tomas_damelio/outputs/DEAP-bids/derivatives/mne-bids-pipeline-eda/eda-cov-matrices-all-freqs/sub-02_covariances_eda.h5')

# %%
