#%%
# open epoched data (clean epochs)and plot
import mne
import matplotlib.pyplot as plt

subject = '01'
epo = mne.read_epochs(f'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-clean_epo.fif')
epo.info

epochsEDA = epo.copy().pick_channels(ch_names=['EDA'])

EDA_var_2022 = epochsEDA.get_data().var(axis=2)[:, 0]  
%matplotlib
plt.plot(EDA_var_2022)
#%%
# This data is really similar to the I plotted in the final scripts
# I will start from raw raw data to see if I can reproduce the results of my thesis regarding True EDA
import mne
import matplotlib.pyplot as plt
import os.path as op


subject = '01'
raw = mne.io.read_raw_bdf(f'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_eeg.bdf')
raw.info

raw.rename_channels(mapping={'GSR1': 'EDA'}) 

raw.set_channel_types({'EDA': 'misc'})


rawEDA = raw.copy().pick_channels(ch_names=['EDA']).load_data()

rawEDA.filter(0.05, 5., fir_design='firwin', picks=['EDA'])

extension = '.fif'
directory_annot = 'outputs/annotations_bad_no_stim/'
fname_fif_annot = op.join(directory_annot, 'sub-' + subject + '_annot' + extension)
annot_from_file = mne.read_annotations(fname = fname_fif_annot, sfreq=512.)

# add annotations to .fif files
rawEDA.set_annotations(annot_from_file)

#%matplotlib
#rawEDA.plot()

epochs = mne.make_fixed_length_epochs(rawEDA,
                                      duration=5.,
                                      overlap =1.,
                                      reject_by_annotation=True,
                                      preload=False)

#%matplotlib
#epochs.plot(picks='EDA')

EDA_var_data = epochs.get_data().var(axis=2)[:, 0] 


#EDA_var_data = EDA_var_data[:-10]

plt.plot(EDA_var_data)
# %%
import autoreject 
from numpy import load

reject_log_data = load('./outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-logsAutoreject_epo.npz')
reject_log = autoreject.autoreject.RejectLog(bad_epochs=reject_log_data['bad_epochs'],
                                            labels=reject_log_data['labels'],
                                            ch_names=reject_log_data['ch_names'])
bad_epochs = reject_log.bad_epochs
bad_epochs_inv = []
for annot in range(len(bad_epochs-1)):
    if bad_epochs[annot] == True:
        bad_epochs_inv.append(False)
    elif bad_epochs[annot] == False:
        bad_epochs_inv.append(True)

epochsEDA = epochs[bad_epochs_inv]

EDA_var_data = epochsEDA.get_data().var(axis=2)[:, 0] 


#EDA_var_data = EDA_var_data[:-10]

plt.plot(EDA_var_data)
# %%
