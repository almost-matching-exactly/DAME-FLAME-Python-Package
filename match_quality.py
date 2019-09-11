# -*- coding: utf-8 -*-
"""
@author: Neha
The purpose of this file is to implement the match quality metric. 
"""

from sklearn.linear_model import Ridge

'''
def compute_ridge_qual(alpha_user=0.1, X, y):
    
    Largely copied/translated from R to Python from Jerry's code: 
    https://github.com/JerryChiaRuiChang/FLAME/blob/master/R/FLAME_bit.R#L125
    
    clf = Ridge(alpha=alpha_user)
    clf.fit(X, y) 
    predicted = clf.predict(X)
    MSE_treated = mean((y - predicted_value)^2)
    
    clf = Ridge(alpha=alpha_user)
    clf.fit(X, y) 
    predicted = clf.predict(X)
    MSE_control = mean((y - predicted_value)^2)
    
    PE = MSE_treated + MSE_control
    
    return PE
'''
def compute_linear_qual(return_matched_group, weight_array):
    ''' This is what I thought the paper was asking for awhile ago.
    This funciton only gets used if you want linear match quality.
    The PE value outputted as an array and described in the README is 
    *NOT* computed here, it's computed in dame_algorithm.py the function
    called decide_drop. I'll probably delete this soon.
    '''
    match_qual_array = []
    temp_qual_val = 0
    for group in return_matched_group:
        for covar_index in range(len(group)):
            if group[covar_index] != '*':
                temp_qual_val += weight_array[covar_index]
        match_qual_array.append(temp_qual_val)
        temp_qual_val = 0
        
    return match_qual_array

'''
def compute_mse(df_all, all_covs, s, weights, outcome_var alpha_user = 0.1):
    
    # So for all of the things not in s, use df_all to run ridge reg and find
    # mse on those values
    
    X = df_all[all_covs-s]
    y = df_all[outcome_var]
    
    clf = Ridge(alpha=alpha_user)
    clf.fit(X, y) 
    predicted = clf.predict(X)
    MSE_treated = mean((y - predicted)^2)
    
    clf = Ridge(alpha=alpha_user)
    clf.fit(X, y) 
    predicted = clf.predict(X)
    MSE_control = mean((y - predicted)^2)
    
    PE = MSE_treated + MSE_control
    
    return PE
'''