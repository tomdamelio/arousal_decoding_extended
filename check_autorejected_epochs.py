#%%
from numpy import load

data = load('./outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-01/eeg/sub-01_task-rest_proc-logsAutoreject_epo.npz')
lst = data.files
for item in lst:
    print(item)
    print(data[item])
# %%
from numpy import load
data = load('./outputs/DEAP-bids/derivatives/mne-bids-pipeline/eda_predictions/02-09--13-51/eda_var_scores--02-09--13-51/sub-01_all_scores_models_DEAP_eda_var_r2_2Fold.npy',
            allow_pickle=True)


# %%
