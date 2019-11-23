# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 07:58:42 2019

@author: Neha
"""


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

    
