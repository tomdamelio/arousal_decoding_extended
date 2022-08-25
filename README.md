# arousal_decoding_extended
We will now describe the necessary steps to run all the analyses of this project.

'''
python convert_DEAP_to_bids.py &&
python create_bad_annotations.py &&
python ../mne-bids-pipeline-main/run.py --config config_deap_eeg.py --steps=preprocessing/frequency_filter && # NOT USED, but genetate copied files that are used by further steps.
python add_annotations_and_channel_info_to_filt_data.py &&
python ../mne-bids-pipeline-main/run.py --config config_deap_eeg.py --steps=preprocessing/make_epochs &&
python ../mne-bids-pipeline-main/run.py --config config_deap_eeg.py --steps=preprocessing/ptp_reject && # NOT USED, but genetate copied files that are used by further steps.
python compute_ssp.py &&
python compute_autoreject.py
'''

python convert_DEAP_to_bids.py && python create_bad_annotations.py && python add_annotations_and_channel_info_to_filt_data.py && python ../mne-bids-pipeline-main/run.py --config config_deap_eeg.py --steps=preprocessing/make_epochs && python ../mne-bids-pipeline-main/run.py --config config_deap_eeg.py --steps=preprocessing/ptp_reject && python compute_ssp.py && python compute_autoreject.py

## Main scripts

- `convert_DEAP_to_bids.py`: Convert DEAP .bdf files into BIDS standard. Runs both on server and locally.
  - **input:** .fif files of DEAP data with info added to raw data, that by default  has to be saved in `./data` directory. If this data is in another directory, it has to be made explicit when running it (e.g. `python convert_DEAP_to_bids.py --deap_data_dir ./Path/To/Original/Data`).
  - **output:** DEAP data in BIDS format, by default saved in './outputs/DEAP-bids'. 

- `create_bad_annotations.py`: 
  - **input**:  DEAP data in BIDS format (directory *should* be 'outputs/DEAP-bids').
  - **output**: annotations files (saved in './outputs/annotations_bad_no_stim/) to be added during preprocessing steps.

- `add_annotations_and_channel_info_to_filt_data.py`: add annotation files to .fif filtered files (after 2nd step of preprocessing).
  - **input**:
    - annotations files (saved in './outputs/annotations_bad_no_stim') .
    - raw .fif files (after maxfilter and frequency filter preprecessing steps). Directory: e.g for subject 01 would be 'outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-01/eeg/sub-01_task-rest_proc-filt_raw.fif'.
  - **output**: raw .fif files (after maxfilter and frequency filter preprocessing steps) with annotations (overwrite raw .fif files without annotations) and cannel info added. EEG + EDA (+ other channels).


- `compute_ssp.py`: detect and remove EOG artifacts from preprocessed data
  - **input**:
    - raw .fif files (after maxfilter and frequency filter preprocessing steps) with annotations e.g for subject 01 would be 'outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-01/eeg/sub-01_task-rest_proc-filt_raw.fif'
    - clean epochs (.fif files). e.g for subject 01 would be 'outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-01/eeg/sub-01_task-rest_proc-clean_epo.fif'
  - **output**: clean epochs after SSP (.fif files). e.g for subject 01 would be 'outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-01/eeg/sub-01_task-rest_proc-SSP_epo.fif'

- `compute_autoreject.py`: compute local version of autoreject.
  - **input**: clean epochs after SSP (.fif files). e.g for subject 01 would be 'outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-01/eeg/sub-01_task-rest_proc-SSP_epo.fif'
  - **output**:
    - clean epoch files after SSP and autoreject (.fif files). e.g. for subject 01 would be 'outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-01/eeg/sub-01_task-rest_proc-autoreject_epo.fif'
    - log files indicating epochs that were rejected after running autoreject (.npz files). e.g. for subject 01 would be 'outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-01/eeg/sub-01_task-rest_proc-logsAutoreject_epo.npz'. We can analyze them using `check_autorejected_epochs.ipynb`

## Auxiliar scripts

- `check_len_stimuli_presentation.py`: check how many trials are detected after running `create_bad_annotations.py`.
- `check_autorejected_epochs.ipynb`: check which epochs where rejected in a particular trial after running `compute_autoreject.py`.
- `check_number_of_final_epochs_after_autoreject.py`

## Deprecated scripts

- `convert_DEAP_to_bids_local.py`: DEPRECATED. Idem to `convert_DEAP_to_bids_server.py` but runs locally.
- `convert_deap_to_bids_without_function`: DEPRECATED. Idem to `convert_DEAP_to_bids_local.py` but runs without functions, parser, ...\- - 
- `add_annotations.py`: add annotation files to .fif filtered files (after 2nd step of preprocessing).
  - **input**:
    - annotations files (saved in './outputs/annotations_bad_no_stim') .
    - raw .fif files (after maxfilter and frequency filter preprecessing steps). Directory: e.g for subject 01 would be 'outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-01/eeg/sub-01_task-rest_proc-filt_raw.fif'.
  - **output**: raw .fif files (after maxfilter and frequency filter preprocessing steps) with annotations (overwrite raw .fif files without annotations).
- `add_channel_info_to_raw_data.py`: Add info to raw data files, i.e. rename channel names, set montage and add frequency of power line.
  - **input:** .bdf files of DEAP data, that by default has to be saved in `./data` directory. 
  - **output:** .fif files of DEAP data with info added to raw data, saved in `./data` directory. 