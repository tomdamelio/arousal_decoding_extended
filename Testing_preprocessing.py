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
# check which channels were dropped before and after autoreject
channels_dropped = []
for subject in subjects:
    epo_before = mne.read_epochs(f'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-SSP_epo.fif')
    epo_before_ch_names = epo_before.info.ch_names
    epo_after = mne.read_epochs(f'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-autoreject_epo.fif')
    epo_after_ch_names = epo_after.info.ch_names
    channels_dropped.append(list(set(epo_before_ch_names).difference(epo_after_ch_names)))
print(channels_dropped)
# %%
# check info epo sub 01
import mne
subject = '01'
epo_before = mne.read_epochs(f'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-SSP_epo.fif')
epo_before.info
# %%
# Check ch_names of sub 01
import mne
subject = '01'
epo = mne.read_epochs(f'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-clean_epo.fif')
epo.info.ch_names
#%%
# check quality of data SUB-01
%matplotlib
epo.plot()
# %%
# Check number of epochs before and after SSP. Should be equal -> they are!
epo_emg = epo.copy().pick_types(emg=True)
# %%
from subject_number import subject_number as subjects
epochs_dropped = []
for subject in subjects:
    epo_before= mne.read_epochs(f'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-clean_epo.fif')
    len_epo_before = len(epo_before)
    epochs_dropped.append(len_epo_before)
    epo_after = mne.read_epochs(f'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-SSP_epo.fif')
    len_epo_after = len(epo_after)
    epochs_dropped.append(len_epo_after)
print(epochs_dropped)
# %%
import mne 
import os.path as op

number_subject = '03'
extension = '.fif'
directory = 'outputs/DEAP-bids/derivatives/mne-bids-pipeline/'
fname_fif = op.join(directory, 'sub-' + number_subject , 'eeg',
                    'sub-' + number_subject + '_task-rest_proc-filt_raw' + extension)
raw = mne.io.read_raw_fif(fname_fif, preload=True) 

%matplotlib
raw.plot()  
#%%

%matplotlib
raw.copy().pick_types(emg=True).plot()
# %%
%matplotlib
raw.copy().pick_channels(ch_names=['EDA']).plot()
# %%

# Filter EDA signal
picks_EDA = mne.pick_channels(raw.info['ch_names'], include=['EDA'])
raw.filter(.05, 5., picks=picks_EDA)

#%%
# Filter EMG signal
picks_EMG = mne.pick_types(raw.info, emg = True)
raw.filter(20., None, picks=picks_EMG)


# %%
# check EDA pochs
import mne
subject = '01'
epo = mne.read_epochs(f'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-EDA_epo.fif')
epo.info
%matplotlib
epo.plot(picks='EDA')
# %%
# check EMG pochs
import mne
subject = '01'
epo = mne.read_epochs(f'C:/Users/dadam/arousal_project/arousal_decoding_extended/outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-' + subject + '/eeg/sub-' + subject + '_task-rest_proc-EMG_epo.fif')
epo.info
%matplotlib
epo.plot(picks=['EXG5', 'EXG6', 'EXG7', 'EXG8'])
# %%
### Reject autorejeted Epochs in EDA EMG and EOG ###
import mne 
from mne_bids import BIDSPath
import config_deap_eeg as cfg
from numpy import load
import autoreject
subject = '01'

bids_path = BIDSPath(subject=subject,
                    session=None,
                    task=cfg.task,
                    datatype=cfg.data_type,
                    extension='.fif',
                    root=cfg.deriv_root)

# Load EDA epochs
epochsEDA_fname = bids_path.copy().update(processing='EDA',
                                            suffix='epo',
                                            check=False)

epochsEDA = mne.read_epochs(epochsEDA_fname, proj=False)

# Load EMG epochs
epochsEMG_fname = bids_path.copy().update(processing='EMG',
                                            suffix='epo',
                                            check=False)  
epochsEMG = mne.read_epochs(epochsEMG_fname, proj=False)

# Load EOG epochs
epochsEOG_fname = bids_path.copy().update(processing='EOG',
                                            suffix='epo',
                                            check=False)   
epochsEOG = mne.read_epochs(epochsEOG_fname, proj=False)

# Load numpy array with autorejected epochs
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

# %%
### Chequear que el len de las epocas de EDA (EMG y EOG) coincidan con las de EEG
import mne 
from mne_bids import BIDSPath
import config_deap_eeg as cfg
from numpy import load
import autoreject
n_epochs={}
subjects=['01','02', '03']
for subject in subjects:

    bids_path = BIDSPath(subject=subject,
                        session=None,
                        task=cfg.task,
                        datatype=cfg.data_type,
                        extension='.fif',
                        root=cfg.deriv_root)

    # Load EEG epochs
    epochsEEG_fname = bids_path.copy().update(processing='autoreject',
                                                suffix='epo',
                                                check=False)

    epochsEEG = mne.read_epochs(epochsEEG_fname, proj=False)

    len_epochsEEG = len(epochsEEG)
    

    # Load EDA epochs
    epochsEDA_fname = bids_path.copy().update(processing='EDA',
                                                suffix='epoRejected',
                                                check=False)

    epochsEDA = mne.read_epochs(epochsEDA_fname, proj=False)

    len_epochsEDA = len(epochsEDA)

    # Load EDA epochs
    epochsEMG_fname = bids_path.copy().update(processing='EMG',
                                                suffix='epoRejected',
                                                check=False)

    epochsEMG = mne.read_epochs(epochsEMG_fname, proj=False)

    len_epochsEMG = len(epochsEMG)

    # Load EDA epochs
    epochsEOG_fname = bids_path.copy().update(processing='EMG',
                                                suffix='epoRejected',
                                                check=False)

    epochsEOG = mne.read_epochs(epochsEMG_fname, proj=False)

    len_epochsEOG = len(epochsEMG)

    n_epochs[subject] = [len_epochsEEG, len_epochsEDA, len_epochsEMG, len_epochsEOG]

    
# %%
