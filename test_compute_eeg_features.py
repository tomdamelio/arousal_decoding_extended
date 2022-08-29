#%%
import h5io
import numpy as np
import pandas as pd
import importlib

#%%
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

#%%
df_subjects = pd.read_csv(bids_root / "participants.tsv", sep='\t')
df_subjects = df_subjects.set_index('participant_id')
df_subjects = df_subjects.sort_index()  

#%%
features = h5io.read_hdf5(
    deriv_root / f'features_{feature_label}_{condition}.h5')
#%%
DEBUG = True
for sub in ['sub-01', 'sub-02', 'sub-03']:
    covs = [features[sub]]
    if DEBUG:
        covs = covs[:30]    
    X_cov = np.array([cc for cc in covs])    
    df_features = pd.DataFrame(
        {band: list(X_cov[:, ii]) for ii, band in
        enumerate(frequency_bands)})
# %%
subjects = ['sub-01', 'sub-02', 'sub-03']
fname_covs = op.join(derivative_path, f'{measure}-cov-matrices-all-freqs', 'sub-' + subject + f'_covariances_{measure}.h5')
covs = mne.externals.h5io.read_hdf5(fname_covs)
for subject in subjects:
    covs
