#%%
import datetime
import importlib
import os
import os.path as op

import h5io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from coffeine import make_filter_bank_regressor
from joblib import Parallel, delayed
from sklearn.linear_model import GammaRegressor, RidgeCV
from sklearn.model_selection import (GridSearchCV, KFold, cross_val_predict,
                                     cross_val_score)
from sklearn.compose import TransformedTargetRegressor
from sklearn.preprocessing import QuantileTransformer, quantile_transform

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

DEBUG = False

################################


derivative_path = deriv_root 
pred_path = derivative_path / f'{measure}_predictions'


date = datetime.datetime.now().strftime("%d-%m--%H-%M")    
n_components = np.arange(1, 32, 1)
seed = 42
n_splits = 5
n_jobs = -1
score_name, scoring = "r2", "r2"
cv_name = '5Fold'

freqs = {
    "delta": (0.1, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 14.0),
    "beta": (14.0, 30.0),
    "gamma": (30.0, 80.0),
}

estimator_type = GammaRegressor()


df_subjects = pd.read_csv(bids_root / "participants.tsv", sep='\t')
df_subjects = df_subjects.set_index('participant_id')
df_subjects = df_subjects.sort_index()  

#features_X = h5io.read_hdf5(deriv_root / f'features_{feature_label}_{condition}.h5')
features_y = h5io.read_hdf5(deriv_root / f'features_EDA_{condition}.h5')

#%%
covs = list()

if DEBUG:
    subjects = ['sub-01','sub-02','sub-03','sub-04','sub-05']
    n_jobs = 4
    debug_out = '_DEBUG'
else:
    subjects = df_subjects.index.values
    subjects = subjects.tolist()
    debug_out = ''

dict_features = {}    

#%%
import matplotlib.pyplot as plt

subjects = ['sub-21']

for subject in subjects:
    
    ###### read peripheral features -> y #####
    # Read EDA data
    eda_features = [features_y[subject]]
    #X_eda_features= np.array([cc for cc in eda_features])
    #X_eda_features = np.squeeze(X_eda_features, axis=0)
        
    y = eda_features[0]['meanEDA_SMNA']
    del eda_features
    y = y[:len(y)-int(len(y)/20)] # Crop last 20th part of signal (considering problems in cvXEDA algorithm)

    ###### read cov matrices -> X #####
    #covs = [features_X[subject]]
    #X_cov = np.array([cc for cc in covs])
    #X_cov = np.squeeze(X_cov, axis=0) 
    #df_features = pd.DataFrame(
    #    {band: list(X_cov[:len(y), ii]) for ii, band in
    #    enumerate(freqs)}) # Crop last 20th part of signals (considering problems in cvXEDA algorithm)
    #del covs
    #del X_cov

    print(subject)
    #print(df_features.shape)
    print(len(y))
    plt.plot(y)
    
# %%
