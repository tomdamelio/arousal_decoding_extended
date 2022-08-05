# arousal_decoding_extended

`convert_DEAP_to_bids_server.py`: file necessary to convert DEAP .bdf files into bids standard. Runs also locally on my PC.
`convert_DEAP_to_bids_local.py`: idem to `convert_DEAP_to_bids_server.py` but runs locally.
`convert_deap_to_bids_without_function`: DEPRECATED. Idem to ut runs without functions, parser, ...
`convert_DEAP_to_bids_local.py`: DEPRECATED. I can also run server file locally.
`freate_bad_annotations.py`: create two files.
1. raw files + annotations (saved in `./outputs/DEAP-bids`)
2. annotations files (saved in `./outputs/annotations_bad_no_stim`)
`check_len_stimuli_presentation.py`: check how many trials are detected after running `create_bad_annotations.py`
`add_annotations.py`: add annot files to .fif filtered files (after 2nd step of preprocessing).

