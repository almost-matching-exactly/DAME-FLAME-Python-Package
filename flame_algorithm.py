# -*- coding: utf-8 -*-
"""
@author: Neha

THIS FILE IS STILL UNDER DEVELOPMENT
"""
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error

import grouped_mr
import dame_algorithm

def decide_drop(all_covs, consider_dropping, prev_dropped, df_all, 
                treatment_column_name, outcome_column_name, df_holdout, 
                adaptive_weights):
    """
    This is the decide drop function. 
    """
    
    # This is where we decide who to drop, and also compute the pe 
    # value that gets outputted in the list described in readme. 
    best_drop = 0
    best_pe = 100000000
    for possible_drop in consider_dropping:
        # S is the frozenset of covars we drop. We try dropping each one
        s = prev_dropped.union(set(possible_drop))
        print(df_holdout.columns.difference(
                                   [outcome_column_name, 
                                    treatment_column_name] + list(s)))
        
        #X-treated is the df that has rows where treated col = 1 and
        # all cols except: outcome/treated/the covs being dropped
        X_treated = df_holdout.loc[df_holdout[treatment_column_name]==1, 
                           df_holdout.columns.difference(
                                   [outcome_column_name, 
                                    treatment_column_name] + list(s))]

        #X-control is the df that has rows where treated col = 0 and
        # all cols except: outcome/treated/the covs being dropped
        X_control = df_holdout.loc[df_holdout[treatment_column_name]==0, 
                           df_holdout.columns.difference(
                                   [outcome_column_name, 
                                    treatment_column_name] + list(s))]

        Y_treated = df_holdout.loc[df_holdout[treatment_column_name]==1, 
                                   outcome_column_name]
        
        Y_control = df_holdout.loc[df_holdout[treatment_column_name]==0, 
                                   outcome_column_name]
        
        if (len(X_treated)==0 or len(X_control) == 0 or \
            len(Y_treated) == 0 or len(Y_control) ==0 or \
            len(X_treated.columns) == 0 or len(X_control.columns) == 0):
            return False, False
       
        if adaptive_weights == "ridge":
            clf = Ridge(alpha=0.1)
        elif adaptive_weights == "decision tree":
            clf = DecisionTreeRegressor()
            
        # Calculate treated MSE
        clf.fit(X_treated, Y_treated) 
        predicted = clf.predict(X_treated)
        MSE_treated = mean_squared_error(Y_treated, predicted)
        
        # Calculate control MSE
        clf.fit(X_control, Y_control) 
        predicted = clf.predict(X_control)
        MSE_control = mean_squared_error(Y_control, predicted)
    
        PE = MSE_treated + MSE_control
        
        # Use the smallest PE as the covariate set to drop.
        if PE < best_pe:
            best_pe = PE
            best_drop = possible_drop
            
    return best_drop, best_pe

def flame_generic(df_all, treatment_column_name, weight_array, outcome_column_name, 
                  adaptive_weights,
                  df_holdout, repeats=True, pre_dame=False):
    '''
    All variables are the same as dame algorithm 1 except for:
    pre_dame(False, integer): Indicates whether the algorithm will move to 
     DAME and after integer number of iterations. 
    '''
    # Initialize variables. These are all moving/temporary throughout algo
    all_covs = df_all.columns.tolist()
    all_covs.remove(treatment_column_name) 
    all_covs.remove(outcome_column_name)
    df_unmatched = df_all.copy(deep=True) 
    all_covs_max_list = [max(df_all[x])+1 for x in all_covs] 
    
    # The items getting returned
    return_covs_list = [] # each index is that iteration's cov list matched on
    return_pe= [] # list of predictive errors, 
                  # one for each item in return_covs_list
                  
    return_matches = pd.DataFrame(columns=all_covs)
    
    # As an initial step, we attempt to match on all covariates
    
    covs_match_on = all_covs
    #covs_max_list = all_covs_max_list
    return_covs_list.append(covs_match_on)
    
    matched_rows, return_matches = grouped_mr.algo2_GroupedMR(df_all, df_unmatched, 
                                                     covs_match_on, all_covs,
                                                     treatment_column_name, 
                                                     outcome_column_name,
                                                     return_matches)
    

    # Now remove the matched units
    df_unmatched.drop(matched_rows.index, inplace=True)
    
    if repeats == False:
        df_all = df_unmatched
    
    
    h = 1 # The iteration number
    
    consider_dropping = set(frozenset([i]) for i in all_covs)
    prev_dropped = set()
    
    # Here, we begin the iterative dropping procedure of FLAME
    while True:
        # Iterates while there are units to match to match in
        try:
            if (1 not in df_unmatched[treatment_column_name].values or \
                0 not in df_unmatched[treatment_column_name].values):
                print("We finished with no more units to match")
                break
        except TypeError:
            break
                
        # quit if there are covariate sets to choose from
        if (len(consider_dropping) == 0):
            break
        
        # We find curr_covar_set, the best covariate to drop. 
        new_drop, pe = decide_drop(all_covs, consider_dropping, prev_dropped, 
                                     df_all, 
                                     treatment_column_name, outcome_column_name,
                                     df_holdout, adaptive_weights)
        
        # Check for error in above step:
        if (new_drop == False):
            break
        
        return_pe.append(pe)                
        
        covs_match_on = list(set(all_covs)-new_drop-prev_dropped)
        
        return_covs_list.append(covs_match_on)
        
        matched_rows, return_matches = grouped_mr.algo2_GroupedMR(df_all, df_unmatched, 
                                                     covs_match_on, all_covs,
                                                     treatment_column_name, 
                                                     outcome_column_name,
                                                     return_matches)
       
        consider_dropping = consider_dropping.difference([new_drop]) 
        prev_dropped.add(new_drop)
        
        # Remove matches.
        df_unmatched = df_unmatched.drop(matched_rows.index, errors='ignore')
 
        if repeats == False:
            df_all = df_unmatched

        h += 1
        print("iteration number: ", h)
        if (pre_dame != False and pre_dame <= h):
            
            # drop the columns that have already been matched on
            for i in prev_dropped:
                df_all = df_all.loc[:, df_all.columns.drop(i)]
                df_holdout = df_holdout.loc[:, df_holdout.columns.drop(i)]
            
            
            # call dame algorithm
            return_matches_dame = dame_algorithm.algo1(df_all, 
                                                       treatment_column_name,
                                                       weight_array,
                                                       outcome_column_name,
                                                       adaptive_weights,
                                                       df_holdout, 
                                                       repeats, want_pe=False)
            
            # return the matches we made here, plus the matches made in dame. 
            return return_matches, return_matches_dame
            
        # end loop. 
    return return_matches
