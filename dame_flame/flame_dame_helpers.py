# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 18:56:00 2019

@author: nrg18
"""
import numpy as np
import pandas as pd

from sklearn.linear_model import Ridge
from sklearn.linear_model import RidgeCV

from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer  

def compute_bf(matched_rows, treatment_column_name, df_unmatched):
    '''
    Helper function to compute the balancing factor
    '''
    
    mg_treated = matched_rows[treatment_column_name].sum()
    mg_control = len(matched_rows) - mg_treated
    available_treated = df_unmatched[treatment_column_name].sum()
    available_control = len(df_unmatched) - available_treated
    
    if (available_treated != 0 and available_control != 0):
        return mg_treated/available_treated + mg_control/available_control
    elif (available_treated == 0):
        return mg_control/available_control
    elif (available_control == 0):
        return mg_treated/available_treated
    

def find_pe_for_covar_set(df_holdout, treatment_column_name, 
                          outcome_column_name, s, adaptive_weights,
                          alpha_given):
    '''
    this is a helper function to decide_drop that will find pe of a given s
    '''
            
    # The iteration and mean of array is only used when doing MICE on holdout
    pe_array = []
    for i in range(len(df_holdout)):
        
        
        X_treated, X_control, Y_treated, Y_control = separate_dfs(
            df_holdout[i], treatment_column_name, outcome_column_name, s)
    
        # error check. If this is true, we stop matching.
        if type(X_treated) == bool:
            return False
        
        if adaptive_weights == "ridge":
            clf = Ridge(alpha=alpha_given)
        elif adaptive_weights == "ridgeCV":
            clf = RidgeCV(alphas=alpha_given)
        elif adaptive_weights == "decision tree":
            clf = DecisionTreeRegressor()
        else:
            return False
        
        # Calculate treated MSE
        clf.fit(X_treated, Y_treated) 
        predicted = clf.predict(X_treated)
        MSE_treated = mean_squared_error(Y_treated, predicted)
        
        # Calculate control MSE
        clf.fit(X_control, Y_control) 
        predicted = clf.predict(X_control)
        MSE_control = mean_squared_error(Y_control, predicted)
    
        pe_array.append(MSE_treated + MSE_control)
        
    PE = np.mean(pe_array)
    return PE

def create_mice_dfs(df_holdout, num_imputes):
    '''
    This creates num_imputes number of imputed datasets
    '''
    df_holdout_array = []
    for i in range(num_imputes):
        imp = IterativeImputer(max_iter=10, random_state=i, 
                               sample_posterior=True, 
                               estimator=DecisionTreeRegressor())
        imp.fit(df_holdout)
        df_holdout_array.append(pd.DataFrame(data=np.round(imp.transform(df_holdout)), 
                                             columns=df_holdout.columns, index=df_holdout.index))
        
    return df_holdout_array
    
def separate_dfs(df_holdout, treatment_col_name, outcome_col_name,
                       covs_include):
    """
    This function serves to create the control/treatment dfs for use 
    in the decide_drop functions in flame and in dame.
    """
    #X-treated is the df that has rows where treated col = 1 and
    # all cols except: outcome/treated/the covs being dropped
    X_treated = df_holdout.loc[df_holdout[treatment_col_name]==1, 
                       df_holdout.columns.difference(
                               [outcome_col_name, 
                                treatment_col_name] + list(covs_include))]

    #X-control is the df that has rows where treated col = 0 and
    # all cols except: outcome/treated/the covs being dropped
    X_control = df_holdout.loc[df_holdout[treatment_col_name]==0, 
                       df_holdout.columns.difference(
                               [outcome_col_name, 
                                treatment_col_name] + list(covs_include))]

    Y_treated = df_holdout.loc[df_holdout[treatment_col_name]==1, 
                               outcome_col_name]
    
    Y_control = df_holdout.loc[df_holdout[treatment_col_name]==0, 
                               outcome_col_name]
    
    # error check. If this is true, we stop matching. 
    if (len(X_treated)==0 or len(X_control) == 0 or \
        len(Y_treated) == 0 or len(Y_control) ==0 or \
        len(X_treated.columns) == 0 or len(X_control.columns) == 0):
        return False, False, False, False
    
    return X_treated, X_control, Y_treated, Y_control
