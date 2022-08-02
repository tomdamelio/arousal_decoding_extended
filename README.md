# arousal_decoding_extended

`convert_DEAP_to_bids_server.py`: file necessary to convert DEAP .bdf files into bids standard. Runs also locally on my PC.
`convert_DEAP_to_bids_local.py`: idem to `convert_DEAP_to_bids_server.py` but runs locally.
`convert_deap_to_bids_without_function`: DEPRECATED. Idem to ut runs without functions, parser, ...
`convert_DEAP_to_bids_local.py`: DEPRECATED. I can also run server file locally.
`add_annotations.py`: create two files.
1. raw files + annotations (saved in `./outputs/DEAP-bids`)
2. annotations files (saved in `./outputs/annotations_bad_no_stim`)
`check_len_stimuli_presentation.py`: check how many trials are detected after running `add_annotations.py`
