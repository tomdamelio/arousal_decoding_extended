#%%
import logging
import os
import os.path as op
import pathlib

import numpy as np
import matplotlib.pyplot as plt
import mne

from subject_number import subject_number
import neurokit2 as nk

# Open data subject 1
number_subject = '03'

# open .fif filtered raw files
extension = '.fif'
directory = 'outputs/DEAP-bids/derivatives/mne-bids-pipeline/'
fname_fif = op.join(directory, 'sub-' + number_subject , 'eeg',
                    'sub-' + number_subject + '_task-rest_proc-filt_raw' + extension)
raw = mne.io.read_raw_fif(fname_fif, preload=True) 
#%%

# Extract just EMG data 
#raw_emg = raw.copy().pick_channels(['EXG5','EXG6']).get_data()
raw_emg_5 = raw.copy().pick_channels(['EXG5']).get_data()

raw_emg_5 = np.squeeze(raw_emg_5)
#raw_emg_5 = raw_emg_5[:1800000]
#plt.plot(raw_emg_5[:750000])


#%%
raw_emg_6 = raw.copy().pick_channels(['EXG6']).get_data()

raw_emg_6 = np.squeeze(raw_emg_6)
#raw_emg_6 = raw_emg_6[:1800000]
#plt.plot(raw_emg_6[:750000])

#%%
#emg_delta = raw_emg_5 - raw_emg_6
#plt.plot(emg_delta[:750000])

#%%
# Perform EMG preprocessing according to neurokit
signals_5, info = nk.emg_process(raw_emg_5, sampling_rate=512)
signals_6, info = nk.emg_process(raw_emg_5, sampling_rate=512)


#signals.head()
# EMG_Raw	EMG_Clean	EMG_Amplitude	EMG_Activity	EMG_Onsets	EMG_Offsets

#%%
#nk.emg_plot(signals.iloc[:20000,:])	
#%%
# Add EMG 
emg_amplitude_5 = signals_5["EMG_Amplitude"]
emg_amplitude_6 = signals_6["EMG_Amplitude"]

emg_amplitude_data = np.concatenate([
    np.atleast_2d(emg_amplitude_5),
    np.atleast_2d(emg_amplitude_6)
])

emg_amplitude_info = mne.create_info(
    ch_names=["EMG_Amplitude_5", "EMG_Amplitude_6"],
    sfreq=raw.info["sfreq"],
    ch_types=["emg", "emg"],
)

emg_amplitude_info["line_freq"] = raw.info["line_freq"]
emg_amplitude_info["subject_info"] = raw.info["subject_info"]

with emg_amplitude_info._unlock():
    emg_amplitude_info["lowpass"] = raw.info["lowpass"]
    emg_amplitude_info["highpass"] = raw.info["highpass"]
    
emg_amplitude_raw = mne.io.RawArray(
    data=emg_amplitude_data,
    info=emg_amplitude_info,
    first_samp=raw.first_samp,
)

#%%
#raw.anonymize()
emg_amplitude_raw.anonymize()

#emg_amplitude_raw.set_meas_date(raw.info["meas_date"])

raw.add_channels([emg_amplitude_raw])


#################################################
# Continue working now on `add_annotations_....py`
#################################################



# %%
