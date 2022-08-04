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

data_type = 'eeg'

#subjects = 'all'
subjects = ['01']

#drop_channels = ['-1', '-0', 'GSR2', 'Erg1', 'Erg2']

eeg_reference = [] 

eeg_template_montage: 'biosemi32'

analyze_channels = 'all'

conditions = ['rest']

l_freq = 0.1
h_freq = 49

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

ssp_reject_eog = 'autoreject_global'

ssp_autoreject_decim = 5

reject = None

reject_tmin = None

reject_tmax = None

autoreject_decim = 4

decode = False

interpolate_bads_grand_average = True

run_source_estimation = False




