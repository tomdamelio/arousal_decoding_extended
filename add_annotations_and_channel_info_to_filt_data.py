#%%
import logging
import os
import os.path as op
import pathlib

import numpy as np
import mne

from subject_number import subject_number

DEBUG = False

if DEBUG:
    subject_number = ['01']
    i = '01'
    
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
        
        picks = mne.pick_types(raw.info, eeg=True, eog=False, stim=False, exclude='bads')
        
        raw.notch_filter(np.arange(50, 250, 50), picks=picks, filter_length='auto',
                phase='zero')
        
        raw.filter(l_freq, h_freq)

        # Export .fif files with annotations
        raw.save(fname = fname_fif, overwrite=True)
    except Exception as e:
        logging.error('Error at %s', exc_info=e)