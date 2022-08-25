from pathlib import Path
import os


study_name = 'arousal_decoding_deap' 
bids_root = Path("./outputs/DEAP-bids")
deriv_root = Path('./outputs/DEAP-bids/derivatives/mne-bids-pipeline')

source_info_path_update = {'processing': 'autoreject',
                           'suffix': 'epo'}

if os.name == 'nt':
    N_JOBS = 4
else:
    N_JOBS = 30

task = 'rest' 

ch_types = ['eeg']

sessions = []

data_type = 'eeg'

subjects = 'all'
#subjects = ['01']

#drop_channels = ['-1', '-0', 'GSR2', 'Erg1', 'Erg2']
drop_channels = ['GSR2', 'Erg1', 'Erg2']

eeg_reference = [] 

eeg_template_montage: 'biosemi32'

#analyze_channels = 'all'
analyze_channels = [
    'Fp1','AF3','F3','F7','FC5','FC1','C3','T7','CP5','CP1',
    'P3','P7','PO3','O1','Oz','Pz','Fp2','AF4',
    'Fz','F4','F8','FC6','FC2','Cz','C4','T8',
    'CP6','CP2','P4','P8','PO4','O2']

conditions = ['rest']

l_freq = None # will specify it in an additional script
h_freq = None # will specify it in an additional script

event_repeated = "drop" 

l_trans_bandwidth = 'auto'

h_trans_bandwidth = 'auto'

random_state = 42

shortest_event = 1

log_level = 'info'

#on_error = 'continue'
on_error = 'debug'

epochs_tmin = 0.

epochs_tmax = 5.

rest_epochs_duration = 5.

rest_epochs_overlap = 1.

baseline =  None 

#spatial_filter = 'ssp'

ssp_reject_eog = 'autoreject_global'

ssp_reject_ecg = 'autoreject_global'

ssp_autoreject_decim = 5

reject = None

reject_tmin = None

reject_tmax = None

autoreject_decim = 4

decode = False

interpolate_bads_grand_average = True

run_source_estimation = False




