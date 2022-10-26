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
    subject_number = ['01', '02', '03', '04', '05']
    
l_freq = 0.1
h_freq = 80.0
#%%

for i in subject_number: 
    try:
        number_subject = i
        
        # open .fif filtered raw files
        extension = '.fif'
        directory = 'outputs/DEAP-bids/derivatives/mne-bids-pipeline/'
        fname_fif = op.join(directory, 'sub-' + number_subject , 'eeg',
                            'sub-' + number_subject + '_task-rest_proc-filt_raw' + extension)
        raw = mne.io.read_raw_fif(fname_fif, preload=True) 
        
        # declare montage
        montage = mne.channels.make_standard_montage(kind="biosemi32", head_size=0.095)   
        
        # Rename channel EDA 
        raw.rename_channels(mapping={'GSR1': 'EDA'})        
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
        # Perform EDA preprocessing according to neurokit
        data_eda = nk.eda_phasic(nk.standardize(raw_eda), sampling_rate=512)
        # add phasic and tonic components to Raw object 
        eda_phasic = data_eda["EDA_Phasic"]
        eda_tonic = data_eda["EDA_Tonic"]
        
        # Extract EMG data 
        raw_emg_5 = raw.copy().pick_channels(['EXG5']).get_data()
        raw_emg_5 = np.squeeze(raw_emg_5)
        raw_emg_6 = raw.copy().pick_channels(['EXG6']).get_data()
        raw_emg_6 = np.squeeze(raw_emg_6)
        # Perform EMG preprocessing according to neurokit
        signals_5, _ = nk.emg_process(raw_emg_5, sampling_rate=512)
        signals_6, _ = nk.emg_process(raw_emg_6, sampling_rate=512)
        emg_amplitude_5 = signals_5["EMG_Amplitude"]
        emg_amplitude_6 = signals_6["EMG_Amplitude"]
        
        # Extract EOG data 
        raw_eog_3 = raw.copy().pick_channels(['EXG3']).get_data()
        raw_eog_3 = np.squeeze(raw_eog_3)
        eog_cleaned = nk.eog_clean(raw_eog_3, sampling_rate=512,  method='neurokit')   

        
        # SEGUIR DESDE ACA -> concateno todas las medidas!
        peripheral_data = np.concatenate([
            np.atleast_2d(eda_phasic),
            np.atleast_2d(eda_tonic),
            np.atleast_2d(emg_amplitude_5),
            np.atleast_2d(emg_amplitude_6),
            np.atleast_2d(eog_cleaned)
        ])

        peripheral_info = mne.create_info(
            ch_names=["EDA_Phasic", "EDA_Tonic", "EMG_Amplitude_5", "EMG_Amplitude_6", "EOG_Cleaned"],
            sfreq=raw.info["sfreq"],
            ch_types=["misc", "misc", "emg", "emg", "eog"]
        )

        peripheral_info["line_freq"] = raw.info["line_freq"]
        peripheral_info["subject_info"] = raw.info["subject_info"]

        with peripheral_info._unlock():
            peripheral_info["lowpass"] = raw.info["lowpass"]
            peripheral_info["highpass"] = raw.info["highpass"]
            
        peripheral_raw = mne.io.RawArray(
            data=peripheral_data,
            info=peripheral_info,
            first_samp=raw.first_samp,
        )
        peripheral_raw.anonymize()
        raw.add_channels([peripheral_raw])

        # Export .fif files with annotations
        raw.save(fname = fname_fif, overwrite=True)
        
    except Exception as e:
        logging.error('Error at %s', exc_info=e)