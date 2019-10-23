# -*- coding: utf-8 -*-
"""
@author: Neha

THIS FILE IS STILL UNDER DEVELOPMENT
"""
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

import grouped_mr
import dame_algorithm

def decide_drop(all_covs, consider_dropping, prev_dropped, df_all, 
                treatment_column_name, outcome_column_name, df_holdout):
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
        print("s", s)
        print(df_holdout.columns.difference(
                                   [outcome_column_name, 
                                    treatment_column_name] + list(s)))
        
        #X-treated is the df that has rows where treated col = 1 and
        # all cols except: outcome/treated/the covs being dropped
        X_treated = df_holdout.loc[df_holdout[treatment_column_name]==1, 
                           df_holdout.columns.difference(
                                   [outcome_column_name, 
                                    treatment_column_name] + list(s))]
        print("X_treated", X_treated)
        print(type(X_treated))
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
        
        print("Y_control", Y_control)
        print(type(Y_control))
        
        print("Y_treated", Y_treated)
        print(type(Y_treated))
        
        if (len(X_treated)==0 or len(X_control) == 0 or \
            len(Y_treated) == 0 or len(Y_control) ==0 or \
            len(X_treated.columns) == 0 or len(X_control.columns) == 0):
            return False, False
        
        print("X_treated: \n", X_treated)
        print("Y_treated: \n", Y_treated)
        
        # Calculate treated MSE
        clf = Ridge(alpha=0.1)
        clf.fit(X_treated, Y_treated) 
        predicted = clf.predict(X_treated)
        MSE_treated = mean_squared_error(Y_treated, predicted)
        
        # Calculate control MSE
        clf = Ridge(alpha=0.1)
        clf.fit(X_control, Y_control) 
        predicted = clf.predict(X_control)
        MSE_control = mean_squared_error(Y_control, predicted)
    
        PE = MSE_treated + MSE_control
        
        # Use the smallest PE as the covariate set to drop.
        if PE < best_pe:
            best_pe = PE
            best_drop = possible_drop
            
    return best_drop, best_pe

def dame_post_flame(df_unmatched, df_matched, prev_dropped, treatment_column_name, 
                    outcome_column_name, repeats, df_all, df_holdout):
    
    adaptive_weights = True
    weights = [0]
    
    unused_covars = set(all_covs).difference(prev_dropped) 
    active_covar_sets = set(frozenset([i]) for i in unused_covars) 
    processed_covar_sets = prev_dropped
    # This I am very confused on. So confused. 
        
    h = 1 # The iteration number
    
    # Her, we begin the iterative dropping procedure of DAME
    while True:
        # Iterates while there is at least one treatment unit to match in
        # TODO: shouldn't there also be at least one control unit to match in? 
        # copute ATT on avg treatment effect on treated (all t have match) 
        # or ATE ate on whole sample, all have match. 
        
        print("df_unmatched: ", df_unmatched)
        
        try:
            if (1 not in df_unmatched[treatment_column_name].values or \
                0 not in df_unmatched[treatment_column_name].values):
                print("We finished with no more units to match")
                break
        except TypeError:
            break
        
        # TODO: Also add early stopping critera based on low match quality.
        
        
        # quit if there are covariate sets to choose from
        if (len(active_covar_sets) == 0):
            break
        
        # We find curr_covar_set, the best covariate set to drop. 
        curr_covar_set, pe = decide_drop(all_covs, active_covar_sets, weights, 
                                     adaptive_weights, df_all, 
                                     treatment_column_name, outcome_column_name,
                                     df_holdout)
        
        # Check for error in above step:
        if (curr_covar_set == False):
            break
                
        # TODO: confirm, do we lose the column ordering in this set operation?                
        covs_match_on = list(set(all_covs)-curr_covar_set)
        # covs_match_on = list(set(curr_covar_set))
        
        return_covs_list.append(covs_match_on)
        
        matched_rows, return_new = grouped_mr.algo2_GroupedMR(df_all, df_unmatched, 
                                                     covs_match_on, all_covs,
                                                     treatment_column_name, 
                                                     outcome_column_name,
                                                     return_new)
        # Generate new active sets
        Z_h = generate_new_active_sets.algo3GenerateNewActiveSets(
                curr_covar_set, processed_covar_sets)
        
        # Remove curr_covar_set from the set of active sets
        active_covar_sets = active_covar_sets.difference([curr_covar_set]) 

        # Update the set of active sets
        active_covar_sets = active_covar_sets.union(Z_h)
        
        # Update the set of already processed covariate-sets. This works bc
        # processed_covar_sets is type set, but curr_covar_set is type frozenset
        processed_covar_sets.add(curr_covar_set)
        
        # Remove matches.
        df_unmatched = df_unmatched.drop(matched_rows.index, errors='ignore')
 
        if repeats == False:
            df_all = df_unmatched

        h += 1
        print("h: ", h)

    

def flame_generic(df_all, treatment_column_name, outcome_column_name, 
                  df_holdout, repeats=True, pre_dame=False):
    '''
    Blah blah blah
    '''
    # Initialize variables. These are all moving/temporary throughout algo
    matched_groups = [] # This is a list of df's. Will be replaced for new output.
    all_covs = df_all.columns.tolist()
    all_covs.remove(treatment_column_name) 
    all_covs.remove(outcome_column_name)
    df_unmatched = df_all.copy(deep=True) 
    all_covs_max_list = [max(df_all[x])+1 for x in all_covs] 
    
    # Indexes the group numbers throughout. 
    group_index = 0
    
    # The items getting returned
    return_covs_list = [] # each index is that iteration's cov list matched on
    return_matched_group = [] # gid & covar list
    return_matched_data = [] # uid and gid list. 
    return_pe= [] # list of predictive errors, 
                  # one for each item in return_covs_list
                  
    # This one is going to replace the other 3 eventually!!:
    return_new = pd.DataFrame(columns=all_covs)
    
    # As an initial step, we attempt to match on all covariates
    
    covs_match_on = all_covs
    #covs_max_list = all_covs_max_list
    return_covs_list.append(covs_match_on)
    
    matched_rows, return_new = grouped_mr.algo2_GroupedMR(
            df_all, df_all, covs_match_on, all_covs, treatment_column_name, outcome_column_name,
                    return_matched_group, return_matched_data, group_index, return_new)
    
    # Now remove the matched units
    df_unmatched.drop(matched_rows.index, inplace=True)
    
    if repeats == False:
        df_all = df_unmatched
    
    
    h = 1 # The iteration number
    
    consider_dropping = set(frozenset([i]) for i in all_covs)
    prev_dropped = set()
    
    # Her, we begin the iterative dropping procedure of FLAME
    while True:
        # Iterates while there is at least one treatment unit to match in
        # TODO: shouldn't there also be at least one control unit to match in? 
        # copute ATT on avg treatment effect on treated (all t have match) 
        # or ATE ate on whole sample, all have match. 
                
        try:
            if (1 not in df_unmatched[treatment_column_name].values or \
                0 not in df_unmatched[treatment_column_name].values):
                print("We finished with no more units to match")
                break
        except TypeError:
            break
        
        # TODO: Also add early stopping critera based on low match quality.
        
        # quit if there are covariate sets to choose from
        if (len(consider_dropping) == 0):
            break
        
        # We find curr_covar_set, the best covariate to drop. 
        new_drop, pe = decide_drop(all_covs, consider_dropping, prev_dropped, 
                                     df_all, 
                                     treatment_column_name, outcome_column_name,
                                     df_holdout)
        
        # Check for error in above step:
        if (new_drop == False):
            break
        
        return_pe.append(pe)                
        
        # TODO: confirm, do we lose the column ordering in this set operation?                
        covs_match_on = list(set(all_covs)-new_drop-prev_dropped)
        # covs_match_on = list(set(curr_covar_set))
        
        return_covs_list.append(covs_match_on)
        
        matched_rows, return_new = grouped_mr.algo2_GroupedMR(df_all, df_unmatched, 
                                                     covs_match_on, all_covs,
                                                     treatment_column_name, 
                                                     outcome_column_name,
                                                     return_matched_group,
                                                     return_matched_data, 
                                                     group_index, return_new)
        # Generate new active sets
        #Z_h = generate_new_active_sets.algo3GenerateNewActiveSets(
        #        curr_covar_set, processed_covar_sets)
        
        # Remove curr_covar_set from the set of active sets
        consider_dropping = consider_dropping.difference(new_drop) 
        prev_dropped.add(new_drop)

        # Update the set of active sets
        # active_covar_sets = active_covar_sets.union(Z_h)
        
        # Update the set of already processed covariate-sets. This works bc
        # processed_covar_sets is type set, but curr_covar_set is type frozenset
        # processed_covar_sets.add(curr_covar_set)
        
        # Remove matches.
        df_unmatched = df_unmatched.drop(matched_rows.index, errors='ignore')
 
        if repeats == False:
            df_all = df_unmatched

        h += 1
        print("h: ", h)
        if (pre_dame != False and pre_dame >= h):
            return dame_post_flame(df_unmatched, df_matched, prev_dropped, 
                                   treatment_column_name, outcome_column_name, repeats,
                                   df_all, df_holdout)

        # end loop. 
    
    # return matched_groups
    # return return_covs_list, return_matched_group, return_matched_data, return_pe, ate
    return return_new
