#%%
import argparse
from multiprocessing import Value

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

####### COMPLETE THIS FUNCTION #######
# SEGUIR DESDE ACA -> USAR LAS FUNCIONES QUE USE PARA MI TESIS PARA SACAR LA FEATURES DE LAS MEDIDAS FISIOLOGICAS
# BUSCAR COMO HIZO TAMBIEN DENIS PARA OBTENER FEATURES HADNCRAFT
def extract_EDA_measures(epochs):
    # 
    if DEBUG:
        #epochs = epochs[:30]
    covs = list()
    for ii in range(len(epochs)):
        features = ...  
        covs.append([c for c in features['covs']])
    features['meta_info'] = meta_info
    return EDA_features # # should be len(epochs) x (2) n_features (meanEDA and VarEDA)

# %%
