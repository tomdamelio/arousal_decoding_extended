#%%
import logging
import os
import os.path as op
import pathlib

import numpy as np
import mne
import neurokit2 as nk

from subject_number import subject_number
from aux_functions import cvxEDA_pyEDA

DEBUG = True

if DEBUG:
    #subject_number = ['02', '03', '04', '05']
    #subject_number = ['06', '07', '08', '09', '10', '11', '12',
    #                    '13', '14', '15', '16', '17', '18', '19',
    #                    '20', '21', '22', '23', '24', '25', '26',
    #                    '27', '28', '29', '30', '31', '32']
    subject_number = ['10']
    
l_freq = 0.1
h_freq = 80.0
#%%

number_subject = '09'

# open .fif filtered raw files
extension = '.fif'
directory = 'outputs/DEAP-bids/derivatives/mne-bids-pipeline/'
fname_fif = op.join(directory, 'sub-' + number_subject , 'eeg',
                    'sub-' + number_subject + '_task-rest_proc-filt_raw' + extension)
raw = mne.io.read_raw_fif(fname_fif, preload=True) 

# declare montage
montage = mne.channels.make_standard_montage(kind="biosemi32", head_size=0.095)   

#%%
####### UNCOMMENT THIS TO RENAME CHANNELS ################
# Rename channel EDA 
#raw.rename_channels(mapping={'GSR1': 'EDA'})        
# Rename other channels
raw.set_channel_types({'EXG1': 'eog',
                        'EXG2': 'eog',
                        'EXG3': 'eog',
                        'EXG4': 'eog',
                        'EXG5': 'emg',
                        'EXG6': 'emg',
                        'EXG7': 'emg',
                        'EXG8': 'emg',
                        'EDA': 'misc',
                        'Resp': 'misc',
                        'Plet': 'misc',
                        'Temp': 'misc'}) 

######### COMMENT THIS TO AVOID CHANNEL DROPING ################

# raw.drop_channels(['EDA_Phasic', 'EDA_Tonic', 'EMG_Amplitude_5', 'EMG_Amplitude_6', 'EOG_Cleaned'])

#%%
################################################################
subject_number = int(number_subject)

if subject_number > 28:
    raw.drop_channels(['-0','-1'])

raw.set_montage(montage)

# open annotations file
extension = '.fif'
directory_annot = 'outputs/annotations_bad_no_stim/'
fname_fif_annot = op.join(directory_annot, 'sub-' + number_subject + '_annot' + extension)
annot_from_file = mne.read_annotations(fname = fname_fif_annot, sfreq=512.)

# add annotations to .fif files
raw.set_annotations(annot_from_file)



# Filter EEG signal
picks = mne.pick_types(raw.info, eeg=True, eog=False, stim=False, exclude='bads')
raw.notch_filter(np.arange(50, 250, 50), picks=picks, filter_length='auto',
        phase='zero')
raw.filter(l_freq, h_freq, picks=picks)

# Extract EDA data 
raw_eda = raw.copy().pick_channels(ch_names=['EDA']).get_data()
raw_eda = np.squeeze(raw_eda)
# %%
import matplotlib.pyplot as plt
plt.plot(raw_eda)
# %%
# SEGUIR DESDE ACA -> POR QUE TOMA COMO INPUT SEÑAL YA FILTRADA EN LOS SUJETOS > 5? REVISAR