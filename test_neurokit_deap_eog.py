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
raw_eog_3 = raw.copy().pick_channels(['EXG3']).get_data()

raw_eog_3 = np.squeeze(raw_eog_3)
#raw_emg_5 = raw_emg_5[:1800000]
plt.plot(raw_eog_3[:750000])


#%%
#emg_delta = raw_emg_5 - raw_emg_6
#plt.plot(emg_delta[:750000])

#%%
# Perform EMG preprocessing according to neurokit
signals = nk.eog_clean(raw_eog_3, sampling_rate=512,  method='neurokit')

#%%

nk.signal_plot([signals[710000:730000]], 
                labels=["Cleaned Signal"])
#%%
# Add EMG 
eog_cleaned = signals

eog_cleaned_data = np.concatenate([
    np.atleast_2d(eog_cleaned)
])

eog_cleaned_info = mne.create_info(
    ch_names=["EOG_Cleaned"],
    sfreq=raw.info["sfreq"],
    ch_types=["eog"],
)

eog_cleaned_info["line_freq"] = raw.info["line_freq"]
eog_cleaned_info["subject_info"] = raw.info["subject_info"]

with eog_cleaned_info._unlock():
    eog_cleaned_info["lowpass"] = raw.info["lowpass"]
    eog_cleaned_info["highpass"] = raw.info["highpass"]
    
eog_cleaned_raw = mne.io.RawArray(
    data=eog_cleaned_data,
    info=eog_cleaned_info,
    first_samp=raw.first_samp,
)

#%%
#raw.anonymize()
eog_cleaned_raw.anonymize()

#emg_amplitude_raw.set_meas_date(raw.info["meas_date"])

raw.add_channels([eog_cleaned_raw])


#################################################
# Continue working now on `add_annotations_....py`
#################################################



# %%
