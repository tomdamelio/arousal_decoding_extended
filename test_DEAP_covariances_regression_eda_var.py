#%%
# Minimal test comparing two version fo EDA data
# 1. before (bad results)
# Open epo file from mne-bids-pipeline-eda
import mne
import matplotlib.pyplot as plt

subject = '02'
epo = mne.read_epochs(f'C:/Users/dadam/OneDrive/Escritorio/tomas_damelio/outputs/DEAP-bids/derivatives/mne-bids-pipeline-eda/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-clean_epo.fif')
epochsEDA = epo.copy().pick_channels(ch_names=['EDA'])
EDA_var = epochsEDA.get_data().var(axis=2)[:, 0] 

fig, ax = plt.subplots(1, 1, figsize=[20, 8])
times = [i for i in range(len(epochsEDA))]
ax.plot(times, EDA_var, color='r', alpha = 0.5)
#ax.plot(times, y_before, color='b', alpha = 0.5, label=f'True {measure}')
ax.set_xlabel('Time (epochsEDA)')
#ax.set_ylabel(f'{measure} {y_stat}')
plt.legend()

# %%
# 2: Thesis -> NON EDA SIGNAL
import mne
import matplotlib.pyplot as plt
subject = '02'
epochs = mne.read_epochs(f'C:/Users/dadam/OneDrive/Escritorio/tomas_damelio/outputs/DEAP-bids/derivatives/mne-bids-pipeline-eda/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-clean_epo.fif')
picks_eda = mne.pick_channels(ch_names = epochs.ch_names ,include=['EDA'])        
epochs = epochs.filter(l_freq = None, h_freq = 5., picks=picks_eda)

y = epochs.get_data().var(axis=2)[:, 0]

fig, ax = plt.subplots(1, 1, figsize=[20, 8])
times = [i for i in range(len(epochs))]
ax.plot(times, y, color='r', alpha = 0.5)
#ax.plot(times, y_before, color='b', alpha = 0.5, label=f'True {measure}')
ax.set_xlabel('Time (epochs)')
#ax.set_ylabel(f'{measure} {y_stat}')
plt.legend()


# %%
