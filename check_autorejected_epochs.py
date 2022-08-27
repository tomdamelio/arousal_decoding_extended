#%%
from numpy import load

data = load('./outputs/DEAP-bids/derivatives/mne-bids-pipeline/sub-01/eeg/sub-01_task-rest_proc-logsAutoreject_epo.npz')
lst = data.files
for item in lst:
    print(item)
    print(data[item])
# %%

