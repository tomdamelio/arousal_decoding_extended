import argparse
from joblib import Parallel, delayed
import pandas as pd

import mne
from mne_bids import BIDSPath
import autoreject

from utils import prepare_dataset

DATASETS = ['deap']
parser = argparse.ArgumentParser(description='Compute autoreject.')
parser.add_argument(
    '-d', '--dataset',
    default=None,
    nargs='+',
    help='the dataset for which preprocessing should be computed')
parser.add_argument(
    '--n_jobs', type=int, default=-1,
    help='number of parallel processes to use (default: Max Jobs)')
args = parser.parse_args()
datasets = args.dataset
n_jobs = args.n_jobs
if datasets is None:
    datasets = list(DATASETS)
print(f"Datasets: {', '.join(datasets)}")

DEBUG = True

def run_subject(subject, cfg):
    deriv_root = cfg.deriv_root
    task = cfg.task
    data_type = cfg.data_type
    session = None
    analyze_channels = cfg.analyze_channels
    conditions = cfg.conditions
    extension='.fif'
    root=cfg.deriv_root

    bp_args = dict(root=root, subject=subject,
                   datatype=data_type, processing="SSP", task=task,
                   check=False, suffix="epo", extension=extension)
    if session:
        bp_args['session'] = session
    bp = BIDSPath(**bp_args)

    ok = 'OK'
    fname = bp.fpath
    if not fname.exists():
        return 'no file'
    epochs = mne.read_epochs(fname, proj=False)
    
    has_conditions = any(cond in epochs.event_id for cond in
                         conditions)

    if not has_conditions:
        return 'no event'
    if any(ch.endswith('-REF') for ch in epochs.ch_names):
        epochs.rename_channels(
            {ch: ch.rstrip('-REF') for ch in epochs.ch_names})

    # XXX Seems to be necessary for TUAB - figure out why
    if 'eeg' in epochs:
        montage = mne.channels.make_standard_montage(kind="biosemi32", head_size=0.095)
        epochs.set_montage(montage)

    if analyze_channels:
        epochs.pick_channels(analyze_channels)

    ar = autoreject.AutoReject(n_jobs=1, cv=5, random_state=42)
    epochs, return_log = ar.fit_transform(epochs, return_log=True)
    # important do do this after autorject but before source localization
    # particularly important as TUAB needs to be re-referenced
    # but on the other hand we want benchmarks to be comparable, hence,
    # re-reference all
    if 'eeg' in epochs:
        epochs.set_eeg_reference('average', projection=True).apply_proj()
    bp_out = bp.copy().update(
        processing="autoreject",
        extension='.fif'
    )
    epochs.save(bp_out, overwrite=True)

    bp_out_log = bp.copy().update(
        processing="logsAutoreject",
        extension='.npz'
    )
    
    return_log.save(bp_out_log, overwrite=True)
    
    return ok
    

for dataset in datasets:
    cfg, subjects = prepare_dataset(dataset)
    print(cfg.session)
    N_JOBS = (n_jobs if n_jobs else cfg.N_JOBS)

    if DEBUG:
        subjects = subjects[22:]
        N_JOBS = 3

    print(f"computing autorejct on {dataset}")
    logging = Parallel(n_jobs=N_JOBS)(
        delayed(run_subject)(sub.split('-')[1], cfg) for sub in subjects)
    out_log = pd.DataFrame({"ok": logging, "subject": subjects})
    out_log.to_csv(cfg.deriv_root / 'autoreject_log.csv')