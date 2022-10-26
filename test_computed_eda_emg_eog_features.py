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
n_splits = 2
n_jobs = -1
score_name, scoring = "r2", "r2"
cv_name = '2Fold'

freqs = {
    "delta": (0.1, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 14.0),
    "beta": (14.0, 30.0),
    "gamma": (30.0, 80.0),
}



df_subjects = pd.read_csv(bids_root / "participants.tsv", sep='\t')
df_subjects = df_subjects.set_index('participant_id')
df_subjects = df_subjects.sort_index()  

#features_X = h5io.read_hdf5(deriv_root / f'features_{feature_label}_{condition}.h5')
features_y = h5io.read_hdf5(deriv_root / f'features_EDA_{condition}.h5')

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
subjects = ['sub-01','sub-02','sub-03','sub-04','sub-05']
for subject in subjects:
       
    # Read EDA data
    eda_features = [features_y[subject]]
    X_eda_features= np.array([cc for cc in eda_features])
    X_eda_features = np.squeeze(X_eda_features, axis=0)  
    y_smna = eda_features[0]['meanEDA_SMNA'] # MODIFICAR PARA SACAR ULTMO 20VO DE LA DATA (PLOTEAR A VER COMO DA)
    #y_phasic = eda_features[0]['meanEDA_Phasic'] # MODIFICAR PARA SACAR ULTMO 20VO DE LA DATA (PLOTEAR A VER COMO DA)
    #y_tonic = eda_features[0]['meanEDA_Tonic'] # MODIFICAR PARA SACAR ULTMO 20VO DE LA DATA (PLOTEAR A VER COMO DA)
    y_smna_crop = y_smna[:len(y_smna)-int(len(y_smna)/20)]
    
        
    y = y_smna_crop
    # Plot the True EDA power and the EDA predicted from EEG data
    fig, ax = plt.subplots(1, 1, figsize=[12, 3])
    times = [i for i in range(len(y))]
    ax.plot(times, y, color='r', alpha = 0.5, label='EDA SMNA')
    ax.set_xlabel('Time (epochs)')
    ax.set_title(f'cvxEDA SMNA - Subject {subject}')
    plt.legend()



#%%
y = y_smna_crop
y_trans = np.log1p(y)

f, (ax0, ax1) = plt.subplots(1, 2)

ax0.hist(y, bins=50, density=True)
ax0.set_xlim([0, 2000])
ax0.set_ylabel("Probability")
ax0.set_xlabel("Target")
ax0.set_title("Target distribution")

ax1.hist(y_trans, bins=50, density=True)
ax1.set_ylabel("Probability")
ax1.set_xlabel("Target")
ax1.set_title("Transformed target distribution")

f.suptitle("Synthetic data", y=0.06, x=0.53)
f.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])

#%%
# SEGUIR DESDE ACA -> APLICAR Quantilize transformers 
# Tira error 
from sklearn.preprocessing import QuantileTransformer, quantile_transform

y_smna_crop
y_trans = quantile_transform(
    pd.DataFrame(y_smna_crop), n_quantiles=900, output_distribution="normal", copy=True
).squeeze()

f, (ax0, ax1) = plt.subplots(1, 2)

ax0.hist(y_smna_crop, bins=100, density=True)
ax0.set_xlim([0, 2000])
ax0.set_ylabel("Probability")
ax0.set_xlabel("Target")
ax0.set_title("Target distribution")

ax1.hist(y_trans, bins=100, density=True)
ax1.set_ylabel("Probability")
ax1.set_xlabel("Target")
ax1.set_title("Transformed target distribution")

f.suptitle("Synthetic data", y=0.06, x=0.53)
f.tight_layout(rect=[0.05, 0.05, 0.95, 0.95])


#%%
    ###### read cov matrices -> X #####
    covs = [features_X[subject]]
    X_cov = np.array([cc for cc in covs])
    X_cov = np.squeeze(X_cov, axis=0) 
    df_features = pd.DataFrame(
        {band: list(X_cov[:len(y_smna_crop), ii]) for ii, band in
        enumerate(freqs)})
    del X_cov
    del covs
# %%
df_features.shape
#%%