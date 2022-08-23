
#%%
import os
import os.path as op
import pathlib

import mne
import numpy as np

from subject_number import subject_number

#%%
def save_bad_resp_and_no_stim_annotations(subject_number  = subject_number,
                                            plot_events = False,
                                            plot_data_bad_no_stim = False,
                                            save_data_bad_no_stim = False,
                                            save_just_no_stim_annotations = True):
    
    """
    Mark and  remove all the events that do not correspond to stimulus
    presentation (e.g. pre-experiement, self-reporting, inter-block interval,
    after last stimulus).
    Possibility of save raw files with annotations, or just save annotations.
    
    Parameters
    ----------
    ### subject_number:  list
        Subjects to analyze.
        Default = subject_number --> all subjects
    ### plot_events: Boolean
        Plot all channels with events marks.
        Default = False
    ### plot_data_bad_no_stim: Boolean
        Plot all channls with bad_no_stim annotations.
        Default = False
    ### save_data_bad_no_stim: Boolean
        Save all channels with bad_no_stim annotations. 
        Default = False
    ### save_just_annotations: Boolean
        Save only the annotations (bad_no_stim and resp annotations)
        without saving Raw data of subjects.
        Default = False
        
    Returns
    -------
    This would change depending on the paramters' setting.
    Possibilities: plots, raw data with annotations, or just the annotations.
    The most important output would be to obtain the annotations to add after
    to original files (if 'save_just_annotations' parameter is set as True).
        
                            
    """ 
    for i in subject_number: 
        
        number_subject = i

        # Read bdf files 
        extension = '.bdf'
        directory = 'outputs/DEAP-bids'
        fname_bdf = op.join(directory, 'sub-' + number_subject , 'eeg',
                            'sub-' + number_subject + '_task-rest_eeg' + extension)
        raw_bdf = mne.io.read_raw_bdf(fname_bdf, preload=True) 
        
        mne.rename_channels(info= raw_bdf.info , mapping={'GSR1':'EDA'})

        raw_bdf.set_channel_types({ 'EXG1': 'eog',
                                    'EXG2': 'eog',
                                    'EXG3': 'eog',
                                    'EXG4': 'eog',  
                                    'EXG5': 'emg',
                                    'EXG6': 'emg',
                                    'EXG7': 'emg',
                                    'EXG8': 'emg',
                                    'EDA' : 'misc',
                                    'GSR2': 'misc',
                                    'Erg1': 'misc',
                                    'Erg2': 'misc',
                                    'Resp': 'misc',
                                    'Plet': 'misc',
                                    'Temp': 'misc'})
            
        # Some subjects had problems with channel names and channel types
        # that is necessary to fix
        if int(i) > 28:
            raw_bdf.rename_channels(mapping={'-1': 'Status'} )
            raw_bdf.drop_channels('-0')
        
        elif int(i) > 23:
            raw_bdf.rename_channels(mapping={'': 'Status'} )
        
        # Create events based on stim channel
        events = mne.find_events(raw_bdf, stim_channel='Status')
        
        
        # ID status assigning based on DEAP documentation (subject 01 to 23)
        if int(i) < 24:
            event_id = { 1: 'rating_screen',
                        2: 'video_synch',
                        3: 'fixation_screen ',
                        4: 'music_stim',
                        5: 'fixation_screen_after',
                        7: 'end_exp'}
        
        # ID status assigning based on visual inspection and comparison with subjects'
        # ID status (subject 24 to 32)
        else:
            event_id = { 1638145: 'rating_screen',
                        1638149: 'fixation_screen_after ',
                        1638147: 'fixation_screen',
                        1638148: 'music_stim',
                        1638146: 'video_synch',
                        1638151: 'end_exp',
                        }
        
        # Create Annotation object based on events' ID    
        annot_from_events = mne.annotations_from_events(
            events=events, event_desc=event_id, sfreq=raw_bdf.info['sfreq'],
            orig_time=raw_bdf.info['meas_date'])
        
        # Set annotations' iD in raw files
        raw_bdf.set_annotations(annot_from_events)
        
        # Plot events' annotations
        if plot_events == True:
            raw_bdf.plot()

        # Programmatically annotate bad signal (signal to drop when epoching)
        """
        bad signal annotate as 'bad_no_stim':
        - Time before the first trial
        - Time between trials 
        - Time between blocks (only one bad_no_stim in each subject)
        - Time after the experimental task
        
        Select:
        - events with stim value == 5 [fix after] or 3 [fixation] for subject 01 to 23
        - events with stim value == 1638149 [fix after] or 1638147 [fixation] for subject 24 to 32
        Between this two events -->  music stimulus
        
        """
        # Select indices of 'fixation screen after trial' events 
        if int(i) < 24:
            # 5 -> fixation screen after trial ID for subject 01 to 23
            rows_fix_after = np.where(events[:,2] == 5)
        else:
            # 1638149 -> fixation screen after trial ID for subject 24 to 32
            rows_fix_after = np.where(events[:,2] == 1638149)
        
        # Select events of fixation screen after trial  based on indices       
        events_fix_after= events[rows_fix_after]
        # As we have these events in datapoints, we have to leverage considering
        # sample frequency
        onset_fix_after = events_fix_after[:,0]/raw_bdf.info['sfreq']     

        # Select indices of 'fixation screen before beginning of trial' events 
        if int(i) < 24:
            rows_fix_before = np.where(events[:,2] == 3)
        else:
            rows_fix_before = np.where(events[:,2] == 1638147)
        
        # Select events of fixation screen before trial based on indices    
        events_fix_before = events[rows_fix_before]
        # As we have these events in datapoints, we have to leverage considering
        # sample frequency
        onset_stim_fix_before = events_fix_before[:,0]/raw_bdf.info['sfreq']
        
        # Select from the 2nd event, becasue then we are going to substract
        # the onset of the fixation cross before stimuli 2 and the onset of the
        # fixation cross of stimuli 1, to obtain duration of bad annotations.
        onset_stim_fix_before_2 = onset_stim_fix_before[1:]
        
        # For subjects 23 to 32, there are more annotations at the beginning
        # of the register. We have to remove them, to make the algorithm work.
        if int(i) > 22:
            # Delete an extra value at the beginning of  onset_stim_fix_before_2 
            onset_stim_fix_before_2 = onset_stim_fix_before_2[1:]
            # Delete two  extra value at the beginning of onset_stim_fix_after_2 
            onset_fix_after = onset_fix_after[2:]
            
        # Delete index 22 from onset_fix_after, because instead of 'videosync' event
        # there is an extra fixation mark at index '22' in subject 28
        if int (i) == 28:
            onset_stim_fix_before_2 = np.delete(onset_stim_fix_before_2, 22)

        # Timestamp (in secs) of the onset of 'fixation cross before stimulus' event     
        onset_stim_fix_before_2 = np.append(onset_stim_fix_before_2,
                                            (len(raw_bdf)/raw_bdf.info['sfreq']))

        # substract the onset of the fixation cross before stimuli 2 and the onset of the
        # fixation cross of stimuli 1, to obtain duration of bad annotations
        # (interstimulus interval)
        diff_onset_music_stim = onset_stim_fix_before_2 - onset_fix_after

        # Select event before first music stimulus. The onset of the fixation cross before
        # the first stimulus correspond to the durecion of the first segment of be marked as 'bad'
        if int(i) > 22:
            # In subjects 23 to 32 there is one extra fixation cross that we want to dismiss
            diff_onset_music_stim = np.append(onset_stim_fix_before[1], diff_onset_music_stim)
        else:
            diff_onset_music_stim = np.append(onset_stim_fix_before[0], diff_onset_music_stim)

        # Add '0' as first event, because we want to annotate from the beginning of the registration
        # to the start of the first music stimulus as bad segment    
        onset_music_stim= np.append(0, onset_fix_after)
        
        if int(i) == 28:
            # 37 stimuli + 1 events (beginning of the registration)
            n_stims = 37+1
        else:
            # 40 stimuli + 1 events (beginning of the registration)
            n_stims = 40+1
        
        # Create annotations corresponding to moments in which no stimuli are presented
        later_annot = mne.Annotations(onset=onset_music_stim,
                                    duration=diff_onset_music_stim,
                                    description=['bad_no_stim']*n_stims)

        # Create raw file with 'bad_no_stim' annotations
        raw2 = raw_bdf.copy().set_annotations(later_annot)
        
        # Plot data with 'bad_no_stim' annotations
        if plot_data_bad_no_stim == True:
            fig_plot_EDA_EEG_bad_no_stim = raw2.plot(start=2488)
            return fig_plot_EDA_EEG_bad_no_stim
            
        # Save data with 'bad_no_stim' annotations
        if save_data_bad_no_stim ==True:
            extension = '.fif'
            directory = 'outputs/DEAP-bids'
            fname_fif_with_annotations = op.join(directory, 'sub-' + number_subject , 'eeg',
                            'sub-' + number_subject + '_task-rest_eeg' + extension)
            raw2.save(fname = fname_fif_with_annotations, overwrite=True)
            
        # # Save just 'bad_no_stim' annotations
        if save_just_no_stim_annotations == True:
            extension = '.fif'
            directory = 'outputs/annotations_bad_no_stim/'
            fname_5 = op.join(directory,'sub-'+ number_subject + '_annot' + extension)
            if not pathlib.Path("outputs/annotations_bad_no_stim/").exists():
                os.makedirs(pathlib.Path("outputs/annotations_bad_no_stim/"))
            later_annot.save(fname = fname_5, overwrite=True)

#%%                                                                         
save_bad_resp_and_no_stim_annotations()
