#%%
# Check number of final epochs after autoreject
import mne
subjects = ['01', '02', '03', '04']
#subjects = ['02']
epochs_len = []
for subject in subjects:
    epo = mne.read_epochs(f'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-SSP_epo.fif')
    epo_len = len(epo)
    epochs_len.append(epo_len)
print(epochs_len)
# %%
# check quality of data SUB-04
%matplotlib
epo.plot()
# %%
subject = '01'
raw = mne.io.read_raw_fif(f'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-filt_raw.fif')
# %%
channels_dropped = []
for subject in subjects:
    epo_before = mne.read_epochs(f'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-SSP_epo.fif')
    epo_before_ch_names = epo_before.info.ch_names
    epo_after = mne.read_epochs(f'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-autoreject_epo.fif')
    epo_after_ch_names = epo_after.info.ch_names
    channels_dropped.append(list(set(epo_before_ch_names).difference(epo_after_ch_names)))
print(channels_dropped)
# %%
