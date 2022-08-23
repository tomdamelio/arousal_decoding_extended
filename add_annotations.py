#%%
import os
import os.path as op
import pathlib

import mne

from subject_number import subject_number

#%%

for i in subject_number: 
    
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
                            'GSR2': 'misc',
                            'Erg1': 'misc',
                            'Erg2': 'misc',
                            'Resp': 'misc',
                            'Plet': 'misc',
                            'Temp': 'misc'}) 

    subject_number = int(number_subject)

    if subject_number > 28:
        raw.rename_channels(mapping={'-1': 'Status'})
        raw.drop_channels('-0')

    elif subject_number > 23:
        raw.rename_channels(mapping={'': 'Status'})
        
    raw.set_channel_types({'Status': 'stim'})
    
    raw.set_montage(montage)
    
    raw.info['line_freq'] = 50  # specify power line frequency as required by BIDS
    
    # open annotations file
    extension = '.fif'
    directory_annot = 'outputs/annotations_bad_no_stim/'
    fname_fif_annot = op.join(directory_annot, 'sub-' + number_subject + '_annot' + extension)
    annot_from_file = mne.read_annotations(fname = fname_fif_annot, sfreq=512.)
    
    # add annotations to .fif files
    raw.set_annotations(annot_from_file)

    # Export .fif files with annotations
    raw.save(fname = fname_fif, overwrite=True)