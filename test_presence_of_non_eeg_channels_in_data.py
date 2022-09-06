#%%
import mne
fname = './outputs/DEAP-bids/sub-01/eeg/sub-01_task-rest_eeg.bdf' 
#fname = './data/s01.bdf
raw = mne.io.read_raw_bdf(fname)
# %%
raw.info
# %%
raw.rename_channels(mapping={'GSR1': 'EDA'})    
# %%
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
# %%
%matplotlib
raw.plot()
# %%
