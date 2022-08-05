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
    raw_fif = mne.io.read_raw_fif(fname_fif, preload=True) 
    
    # open annotations file
    extension = '.fif'
    directory_annot = 'outputs/annotations_bad_no_stim/'
    fname_fif_annot = op.join(directory_annot, 'sub-' + number_subject + '_annot' + extension)
    annot_from_file = mne.read_annotations(fname = fname_fif_annot, sfreq=512.)
    
    # add annotations to .fif files
    raw_fif.set_annotations(annot_from_file)

    # Export .fif files with annotations
    raw_fif.save(fname = fname_fif, overwrite=True)