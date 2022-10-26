#%%
import mne
import matplotlib.pyplot as plt
#%%
# clean-epo-files (THIS IS *NOT* THE FILE)
subject = '02'
epo = mne.read_epochs(f'C:/Users/dadam/OneDrive/Escritorio/tomas_damelio/outputs/DEAP-bids/derivatives/mne-bids-pipeline-eda/clean-epo-files/sub-' + subject + '_task-rest_proc-clean_epo.fif')
epo.info

#%%
#
epochsEDA = epo.copy().pick_channels(ch_names=['EDA'])
EDA_var = epochsEDA.get_data().var(axis=2)[:, 0] 
#%%
plt.plot(EDA_var)
# %%
import mne
import matplotlib.pyplot as plt
# Open epoched files from thesis (clean epo eda files) -> THIS IS THE FILE
subject = '01'
epo = mne.read_epochs(f'C:/Users/dadam/OneDrive/Escritorio/tomas_damelio/outputs/DEAP-bids/derivatives/mne-bids-pipeline-eda/clean-epo-files-eda/sub-' + subject + '_task-rest_proc-clean_epo.fif')
epo.info
epochsEDA = epo.copy().pick_channels(ch_names=['EDA'])
EDA_var_eda_files = epochsEDA.get_data().var(axis=2)[:, 0] 
#%%
%matplotlib
plt.plot(EDA_var_eda_files)

# %%
picks_eda = mne.pick_channels(ch_names = epochsEDA.ch_names ,include=['EDA'])     
epochsEDA = epochsEDA.filter(l_freq = None, h_freq = 5., picks=picks_eda)
y = epochsEDA.get_data().var(axis=2)[:, 0]    
%matplotlib
plt.plot(EDA_var_eda_files)

#%%
# Open epo file from mne-bids-pipeline-eda
import mne
import matplotlib.pyplot as plt

# clean-epo-files (THIS IS *NOT* THE FILE)
subject = '01'
epo = mne.read_epochs(f'C:/Users/dadam/OneDrive/Escritorio/tomas_damelio/outputs/DEAP-bids/derivatives/mne-bids-pipeline-eda/sub-01/eeg/sub-' + subject + '_task-rest_proc-clean_epo.fif')
epo.info


epochsEDA = epo.copy().pick_channels(ch_names=['EDA_Phasic']) #, 'EDA_Tonic', 'EDA_SMNA'])
EDA_var = epochsEDA.get_data().var(axis=2)[:, 0] 

plt.plot(EDA_var)
# %%
import numpy as np
def reject_outliers(data, m = 30.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return data[s<m]
EDA_var_rej = reject_outliers(EDA_var)
plt.plot(EDA_var_rej[:200])
# %%
