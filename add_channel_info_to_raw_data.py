#%%
import mne
from subject_number import subject_number


DEBUG = False

if DEBUG:
    subject_number = ['01']


for subject in subject_number: 
        
    fname = f'./data/s{subject}.bdf'    
    raw = mne.io.read_raw_bdf(fname)
    
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

    subject_number = int(subject)

    if subject_number > 28:
        raw.rename_channels(mapping={'-1': 'Status'})
        raw.drop_channels('-0')

    elif subject_number > 23:
        raw.rename_channels(mapping={'': 'Status'})
        
    raw.set_channel_types({'Status': 'stim'})
    
    raw.set_montage(montage)
    
    raw.info['line_freq'] = 50  # specify power line frequency as required by BIDS
    
    fname_fif = f'./data/s{subject}.fif'  

    # Export .fif files with annotations
    raw.save(fname = fname_fif, overwrite=True)
# %%
