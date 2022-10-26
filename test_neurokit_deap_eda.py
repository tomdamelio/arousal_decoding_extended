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

# Rename channel EDA 
#raw.rename_channels(mapping={'GSR1': 'EDA'})        
# Rename other channels
#raw.set_channel_types({'EXG1': 'eog',
#                        'EXG2': 'eog',
#                        'EXG3': 'eog',
#                        'EXG4': 'eog',
#                        'EXG5': 'emg',
#                        'EXG6': 'emg',
#                        'EXG7': 'emg',
#                        'EXG8': 'emg',
#                        'EDA': 'misc',
#                        'Resp': 'misc',
#                        'Plet': 'misc',
#                        'Temp': 'misc'}) 

#%%
# Extract just EDA data 
raw_eda = raw.copy().pick_channels(ch_names=['EDA']).get_data()
raw_eda = np.squeeze(raw_eda)
plt.plot(raw_eda)


#%%
# Perform EDA preprocessing according to neurokit
signals, info = nk.eda_process(raw_eda, sampling_rate=512)

signals.head()

# Extraer EDA "limpio" and features del SCR
cleaned = signals["EDA_Clean"]
features = [ info["SCR_Peaks"]]


# Plot signal comparing EDA raw and filter EDA
%matplotlib inline

# Seteamos parámetros para hacer las imagenes de matplotlib más grandes
plt.rcParams['figure.figsize'] = [30, 5] 
plot = nk.events_plot(features, cleaned, color=['red'])

#%%
data_eda = nk.eda_phasic(nk.standardize(raw_eda), sampling_rate=250)
data_eda["EDA_Raw"] = raw_eda  # Add raw signal
data_eda.plot()

#%%
data_eda["EDA_Phasic"].plot()

#%%
# add phasic and tonic components to Raw (`raw`) object -> ver dscusion en github de Richard (INRIA)

# Add GSR and temperature channels
eda_phasic = data_eda["EDA_Phasic"]
eda_tonic = data_eda["EDA_Tonic"]

eda_phasic_and_tonic_data = np.concatenate([
    np.atleast_2d(eda_phasic),
    np.atleast_2d(eda_tonic),
])

eda_phasic_and_tonic_info = mne.create_info(
    ch_names=["EDA_Phasic", "EDA_Tonic"],
    sfreq=raw.info["sfreq"],
    ch_types=["misc", "misc"],
)

eda_phasic_and_tonic_info["line_freq"] = raw.info["line_freq"]
eda_phasic_and_tonic_info["subject_info"] = raw.info["subject_info"]

with eda_phasic_and_tonic_info._unlock():
    eda_phasic_and_tonic_info["lowpass"] = raw.info["lowpass"]
    eda_phasic_and_tonic_info["highpass"] = raw.info["highpass"]
    
eda_phasic_and_tonic_raw = mne.io.RawArray(
    data=eda_phasic_and_tonic_data,
    info=eda_phasic_and_tonic_info,
    first_samp=raw.first_samp,
)
raw.add_channels([eda_phasic_and_tonic_raw])


#################################################
# Continue working now on `add_annotations_....py`
#################################################



# %%
