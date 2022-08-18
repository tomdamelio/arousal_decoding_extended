import importlib
from types import SimpleNamespace
import pandas as pd

def prepare_dataset(dataset):
    config_map = {'deap': "config_deap_eeg"}
    if dataset not in config_map:
        raise ValueError(
            f"We don't know the dataset '{dataset}' you requested.")

    cfg_in = importlib.import_module(config_map[dataset])
    cfg_out = SimpleNamespace(
        bids_root=cfg_in.bids_root,
        deriv_root=cfg_in.deriv_root,
        task=cfg_in.task,
        analyze_channels=cfg_in.analyze_channels,
        data_type=cfg_in.data_type,
        #subjects_dir=cfg_in.subjects_dir
    )
    cfg_out.conditions = {  # use for epoching
        'deap': ('rest',)
    }[dataset]
    cfg_out.feature_conditions = {  # use for selecting data for features
        'deap': ('rest',)
    }[dataset]

    cfg_out.session = ''
    sessions = cfg_in.sessions

    subjects_df = pd.read_csv(cfg_out.bids_root / "participants.tsv", sep='\t')
    subjects = sorted(sub for sub in subjects_df.participant_id if
                      (cfg_out.deriv_root / sub / cfg_out.session /
                       cfg_out.data_type).exists())

    return cfg_out, subjects