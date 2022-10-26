#%%
import datetime
import importlib
import os
import os.path as op

import h5io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from coffeine import make_filter_bank_regressor
from joblib import Parallel, delayed
from sklearn.linear_model import GammaRegressor, RidgeCV
from sklearn.model_selection import (GridSearchCV, KFold, cross_val_predict,
                                     cross_val_score)

dataset =  'deap'
config_map = {'deap': "config_deap_eeg"}

cfg = importlib.import_module(config_map[dataset])
bids_root = cfg.bids_root
deriv_root = cfg.deriv_root
analyze_channels = cfg.analyze_channels

condition = 'rest'
feature_label = 'fb_covs'

#########  SET CONFIGS #########

# eda or emg?    
measure = 'eda'
# var or mean?   
y_stat = 'mean'

DEBUG = False

################################


derivative_path = deriv_root 
pred_path = derivative_path / f'{measure}_predictions'

#%%


date = datetime.datetime.now().strftime("%d-%m--%H-%M")    
n_components = np.arange(1, 32, 1)
seed = 42
n_splits = 2
n_jobs = -1
score_name, scoring = "r2", "r2"
cv_name = '2Fold'

freqs = {
    "delta": (0.1, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 14.0),
    "beta": (14.0, 30.0),
    "gamma": (30.0, 80.0),
}

#if y_stat == 'mean' or measure == 'eda':
if y_stat == 'mean' or measure == 'eda':
    estimator_type = RidgeCV(alphas=np.logspace(-3, 5, 100))
else:
    estimator_type = GammaRegressor()

pipelines = {'riemann': make_filter_bank_regressor(
                names=freqs.keys(),
                method='riemann',
                projection_params=dict(scale=1, reg=1.e-05, n_compo=31),
                vectorization_params=dict(metric='riemann'),
                estimator=estimator_type),
            'spoc': make_filter_bank_regressor(
                names=freqs.keys(),
                method='spoc',
                projection_params=dict(scale='auto', reg=1.e-05, shrink=1, n_compo=31),
                vectorization_params=None,
                estimator=estimator_type),
            'log_diag': make_filter_bank_regressor(
                names=freqs.keys(),
                method='log_diag',
                projection_params=None,
                vectorization_params=None,
                estimator=estimator_type),
            'upper': make_filter_bank_regressor(
                names=freqs.keys(),
                method='naive',
                projection_params=None,
                vectorization_params=None,
                estimator=estimator_type),
            'random': make_filter_bank_regressor(
                names=freqs.keys(),
                method='random',
                projection_params=None,
                vectorization_params=None,
                estimator=estimator_type)}

def run_low_rank(n_components, X, y, estimators, cv, scoring):   
    out = dict(n_components=n_components)
    for key, estimator in estimators.items():
        this_est = estimator
        for n_pipeline in range(len(freqs)):
            this_est.steps[0][1].transformers[n_pipeline][1].steps[0][1].n_compo = n_components
        scores = cross_val_score(X=df_features, y=y, estimator=estimator,
                                cv=cv, n_jobs=min(n_splits, n_jobs),
                                scoring=scoring)
        if scoring == 'neg_mean_absolute_error':
            scores = -scores
            print(scores)
        out[key] = scores
    return out

df_subjects = pd.read_csv(bids_root / "participants.tsv", sep='\t')
df_subjects = df_subjects.set_index('participant_id')
df_subjects = df_subjects.sort_index()  

features_X = h5io.read_hdf5(deriv_root / f'features_{feature_label}_{condition}.h5')
features_y = h5io.read_hdf5(deriv_root / f'features_EDA_{condition}.h5')

covs = list()

if DEBUG:
    subjects = ['sub-01','sub-02','sub-03']
    n_jobs = 4
    debug_out = '_DEBUG'
else:
    subjects = df_subjects.index.values
    subjects = subjects.tolist()
    debug_out = ''
    
dict_features = {}    

#%%

for subject in subjects:
    ###### read cov matrices -> y #####
    covs = [features_X[subject]]
    X_cov = np.array([cc for cc in covs])
    X_cov = np.squeeze(X_cov, axis=0) 
    df_features = pd.DataFrame(
        {band: list(X_cov[:, ii]) for ii, band in
        enumerate(freqs)})
    
    ###### read peripheral features -> X #####

    # Read EDA data
    eda_features = [features_y[subject]]
    X_eda_features= np.array([cc for cc in eda_features])
    X_eda_features = np.squeeze(X_eda_features, axis=0)  
    y = eda_features[0]['meanEDA_Tonic']


    low_rank_estimators = {k: v for k, v in pipelines.items()
                            if k in ('spoc', 'riemann')}
    
    cv = KFold(n_splits=n_splits)
    
    out_list = Parallel(n_jobs=n_jobs)(delayed(run_low_rank)(
                        n_components=cc, X=df_features, y=y,
                        cv=cv, estimators=low_rank_estimators, scoring='r2')
                        for cc in n_components)
    
    out_frames = list()
    for this_dict in out_list:
        this_df = pd.DataFrame({'spoc': this_dict['spoc'],
                                'riemann': this_dict['riemann']})
        this_df['n_components'] = this_dict['n_components']
        this_df['fold_idx'] = np.arange(len(this_df))
        out_frames.append(this_df)
    out_df = pd.concat(out_frames)
    
    opt_dir = op.join(pred_path, date, measure + '_' + y_stat + '_opt--' + date)
    if not os.path.exists(opt_dir):
        os.makedirs(opt_dir)
    
    out_df.to_csv(op.join(opt_dir, subject + '_' + dataset + '_component_scores_' +
                            measure + '_' + y_stat + debug_out + '.csv'))

    mean_df = out_df.groupby('n_components').mean().reset_index()
    best_components = {
        'spoc': mean_df['n_components'][mean_df['spoc'].argmax()],
        'riemann': mean_df['n_components'][mean_df['riemann'].argmax()]
    }
        
    pipelines[f"spoc_{best_components['spoc']}"] = make_filter_bank_regressor(
                                        names=freqs.keys(),
                                        method='spoc',
                                        projection_params=dict(scale='auto', reg=1.e-05,
                                                                shrink=1,
                                                                n_compo= best_components['spoc']),
                                        vectorization_params=None,
                                        estimator=estimator_type)

    pipelines[f"riemann_{best_components['riemann']}"] = make_filter_bank_regressor(
                                        names=freqs.keys(),
                                        method='riemann',
                                        projection_params=dict(scale=1, reg=1.e-05,
                                                                n_compo= best_components['riemann']),
                                        vectorization_params=dict(metric='riemann'),
                                        estimator=estimator_type)

    all_scores = dict() 
    for key, estimator in pipelines.items():
        if measure == 'emg': 
            param_grid = {'gammaregressor__alpha': [0.01, 1., 10.]}
            search = GridSearchCV(pipelines[key], param_grid)
            search.fit(df_features, y)
            print(search.best_params_['gammaregressor__alpha'])
            estimator.steps[-1] = ('gammaregressor',
                                    GammaRegressor(alpha = search.best_params_['gammaregressor__alpha'],
                                                    max_iter=1000))
            if 'spoc_' in key:
                spoc_opt_alpha = search.best_params_['gammaregressor__alpha']
            if 'riemann_' in key:
                riemann_opt_alpha = search.best_params_['gammaregressor__alpha']
    
        scores = cross_val_score(X=df_features, y=y, estimator=estimator,
                                cv=cv, n_jobs=min(n_splits, n_jobs),
                                scoring=scoring)
        if scoring == 'neg_mean_absolute_error':
            scores = -scores
            print(scores)
        all_scores[key] = scores
    
    scores_dir = op.join(pred_path, date, measure + '_' + y_stat + '_scores--' + date)
    if not os.path.exists(scores_dir):
        os.makedirs(scores_dir)
    
    np.save(op.join(scores_dir, subject + '_all_scores_models_DEAP_' + measure + '_' +
                            y_stat + '_' + score_name + '_' + cv_name + debug_out + '.npy'),
            all_scores)
    
    y_and_y_pred_opt_models = dict() 
    y_and_y_pred_opt_models['y'] = y
    for model in  ('spoc', 'riemann'):      
        if model == 'spoc':
            if measure == 'emg':
                estimator_spoc_opt = GammaRegressor(alpha = spoc_opt_alpha, max_iter=1000)
            else:
                estimator_spoc_opt = None        
            clf = make_filter_bank_regressor(
                                    names=freqs.keys(),
                                    method='spoc',
                                    projection_params=dict(scale='auto', reg=1.e-05,
                                    shrink=1, n_compo= best_components['spoc']),
                                    vectorization_params=None,
                                    estimator=estimator_spoc_opt)   
            score_opt = np.asarray([v for k,v in all_scores.items() if 'spoc_'in k]).mean().round(3)
        elif model == 'riemann':
            if measure == 'emg':
                estimator_riemann_opt = GammaRegressor(alpha = riemann_opt_alpha, max_iter=1000)
            else:
                estimator_riemann_opt = None
            clf = make_filter_bank_regressor(
                                names=freqs.keys(),
                                method='riemann',
                                projection_params=dict(scale=1, reg=1.e-05,
                                                        n_compo= best_components['riemann']),
                                vectorization_params=dict(metric='riemann'),
                                estimator=estimator_riemann_opt)
            score_opt = np.asarray([
                v for k,v in all_scores.items() if 'riemann_'in k]).mean().round(3)

        # Run cross validaton
        y_preds = cross_val_predict(clf, df_features, y, cv=cv)
        y_and_y_pred_opt_models[model] = y_preds
        
        # Plot the True EDA power and the EDA predicted from EEG data
        fig, ax = plt.subplots(1, 1, figsize=[20, 8])
        times = [i for i in range(len(y))]
        ax.plot(times, y, color='r', alpha = 0.5, label=f'True {measure}')
        ax.plot(times, y_preds, color='b', alpha = 0.5, label=f'Predicted {measure}')
        ax.set_xlabel('Time (epochs)')
        ax.set_ylabel(f'{measure} {y_stat}')
        ax.set_title(f'{subject} - {model} model - {measure} prediction\nR2 = {score_opt}')
        plt.legend()
        
        plot_dir = op.join(pred_path, date, measure + '_' + y_stat + '_plot--' + date)
        if not os.path.exists(plot_dir):
            os.makedirs(plot_dir)
            
        plt_path = op.join(plot_dir, subject + '_' + measure + '_' + y_stat +
                           '_DEAP_plot_prediction_' + model + debug_out + '.png')
        plt.savefig(plt_path)
        
    np.save(op.join(scores_dir, subject + '_' + measure + '_' + y_stat +
                    '_y_and_y_pred_opt_models' + debug_out + '.npy'),
            y_and_y_pred_opt_models)
        
    del pipelines[f"spoc_{best_components['spoc']}"]
    del pipelines[f"riemann_{best_components['riemann']}"]