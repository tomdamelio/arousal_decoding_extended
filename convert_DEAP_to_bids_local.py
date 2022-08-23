#%%
import argparse
import os
import pathlib
from pathlib import Path

import mne
from joblib import Parallel, delayed
from mne_bids import BIDSPath, make_report, print_dir_tree, write_raw_bids

from subject_number import subject_number as subject_ids

#%%
def convert_deap_to_bids(deap_data_dir, bids_save_dir, n_jobs=1, DEBUG=False):
    """Convert DEAP dataset to BIDS format.
    Parameters
    ----------
    deap_data_dir : str
        Directory where the original DEAP dataset is saved, e.g.
        `C:/Users/dadam/OneDrive/Escritorio/tomas_damelio/data`.
    bids_save_dir : str
        Directory where to save the BIDS version of the dataset.
    n_jobs : None | int
        Number of jobs for parallelization.
    """
    subjects_ = subject_ids
    
    if DEBUG:
        subjects_ = subject_ids[:1]
        
    if not bids_save_dir.exists():
        os.makedirs(bids_save_dir)
    
    Parallel(n_jobs=n_jobs)(
        delayed(_convert_subject)(subject, deap_data_dir, bids_save_dir)
        for subject in subjects_) 

#%%
def _convert_subject(subject, data_path, bids_save_dir):
    """Get the work done for one subject"""
    try:
        fname = pathlib.Path(data_path) / f"S{subject}.bdf"    
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
            
        #raw.set_channel_types({ 'Status': 'stim'})
        
        raw.set_montage(montage)
        
        raw.info['line_freq'] = 50  # specify power line frequency as required by BIDS

        # Create events based on stim channel
        events = mne.find_events(raw, stim_channel='Status')
        
        

        if subject_number < 24:
            event_id = {'rating_screen': 1,
                        'video_synch': 2,
                        'fixation_screen': 3,
                        'music_stim': 4,
                        'fixation_screen_after': 5,
                        'unknown': 6,
                        'unknown2': 65536,
                        'end_exp': 7}
        else:
            event_id = {'rating_screen': 1638145,
                        'fixation_screen_after': 1638149,
                        'fixation_screen': 1638147,
                        'music_stim': 1638148,
                        'video_synch': 1638146,
                        'end_exp': 1638151,
                        'unknown_1': 5832448,
                        'unknown_2': 5832449,
                        'unknown_3': 5832451,
                        'unknown_4': 5832452,
                        'unknown_5': 5832453}

        bids_path = BIDSPath(
            subject=subject, task='rest',root=bids_save_dir)

        write_raw_bids(
            raw,
            bids_path,
            events_data=events,
            event_id=event_id,
            overwrite=True
            )
    except Exception as err:
        print(err)
    return subject
#%%
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert DEAP to BIDS.')
    parser.add_argument(
        '--deap_data_dir', type=str,
        default='C:/Users/dadam/OneDrive/Escritorio/tomas_damelio/data',
        help='Path to the original data.')
    parser.add_argument(
        '--bids_save_dir', type=str,
        default=pathlib.Path("./outputs/DEAP-bids"),
        help='Path to where the converted data should be saved.')
    parser.add_argument(
        '--n_jobs', type=int, default=1,
        help='number of parallel processes to use (default: 1)')
    parser.add_argument(
        '--DEBUG', type=bool, default=False,
        help='activate debugging mode')
    args = parser.parse_args()

    convert_deap_to_bids(
        args.deap_data_dir, args.bids_save_dir, n_jobs=args.n_jobs,
        DEBUG=args.DEBUG)
    
    print_dir_tree(args.deap_data_dir)
    print(make_report(args.deap_data_dir))



# %%
