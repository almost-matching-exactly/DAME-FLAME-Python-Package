# -*- coding: utf-8 -*-
"""
@author: Neha
"""
import pandas as pd

# delete this one later:
import time

import grouped_mr
import dame_algorithm
import flame_dame_helpers

def decide_drop(all_covs, consider_dropping, prev_dropped, df_all, 
                treatment_column_name, outcome_column_name, df_holdout_array, 
                adaptive_weights, weights, alpha_given):
    """
    This is the decide drop function. 
    """
    
    # This is where we decide who to drop, and also compute the pe 
    # value that gets outputted in the list described in readme. 
    best_drop = 0
    best_pe = 100000000
    if adaptive_weights == False:
        # todo: repetition in this function with dame. create helper.
        # Iterate through covars, drop one at a time and sum weights.
        max_weight = 0
        for possible_drop in consider_dropping:
            # S is the frozenset of covars we drop. We try dropping each one
             s = prev_dropped.union([possible_drop])
             temp_weight = 0
             for cov_index in range(len(all_covs)):
                 if all_covs[cov_index] not in s:
                     # if an item not in s, add weight. finding impact of drop s
                     temp_weight += weights[cov_index]
             if temp_weight >= max_weight:
                 max_weight = temp_weight
                 best_drop = possible_drop # This is the items we will drop, that will
                 # not get used in the match
        best_pe = max_weight

                
    else:
        for possible_drop in consider_dropping:
            # S is the frozenset of covars we drop. We try dropping each one
            s = prev_dropped.union(set(possible_drop))
            
            PE = flame_dame_helpers.find_pe_for_covar_set(df_holdout_array, 
                                                          treatment_column_name, 
                          outcome_column_name, s, adaptive_weights, alpha_given)
            
            # error check
            if PE == False:
                return False, False
            
            # Use the smallest PE as the covariate set to drop.
            if PE < best_pe:
                best_pe = PE
                best_drop = possible_drop
            
    return best_drop, best_pe

def flame_generic(df_all, treatment_column_name, weights,
                  outcome_column_name, adaptive_weights, alpha,
                  df_holdout, repeats, want_pe,
                  verbose, want_bf, missing_holdout_replace, early_stops,
                  pre_dame):
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
    
    # The items getting returned
    return_pe= [] # list of predictive errors, 
    return_bf = []
                  
    # todo delete this comment later -- justupdated line
    return_matches = pd.DataFrame(columns=all_covs, index=df_all.index)
    
    # As an initial step, we attempt to match on all covariates
    
    covs_match_on = all_covs
    
    matched_rows, return_matches = grouped_mr.algo2_GroupedMR(df_all, df_unmatched, 
                                                     covs_match_on, all_covs,
                                                     treatment_column_name, 
                                                     outcome_column_name,
                                                     return_matches)
    

    # Now remove the matched units
    df_unmatched.drop(matched_rows.index, inplace=True)
    
    if repeats == False:
        df_all = df_unmatched
    
    # set up all the extra dfs if needed
    if missing_holdout_replace != False:
        # now df_holdout is actually an array of imputed datasets
        df_holdout_array = flame_dame_helpers.create_mice_dfs(df_holdout, missing_holdout_replace)
    else:
        # df_holdout_array exists regardless, just size 1 and equal to itself
        # if not doing mice. 
        df_holdout_array = list()
        df_holdout_array.append(df_holdout)
    
    h = 1 # The iteration number
    tot_treated = df_all[treatment_column_name].sum()
    tot_control = len(df_all) - tot_treated
    
    consider_dropping = set(i for i in all_covs)
    prev_dropped = set()
    
    start_time = time.time()
    
    # Here, we begin the iterative dropping procedure of FLAME
    while True:
        # Iterates while there are units to match to match in
        try:
            if early_stops.unmatched_t == True and (1 not in df_unmatched[treatment_column_name].values): 
                print("We finished with no more units to match")
                break
            
            if early_stops.unmatched_c == True and (0 not in df_unmatched[treatment_column_name].values):
                print("We finished with no more units to match")
                break
        except TypeError:
            break
        
        # Hard stop criteria: exceeded the number of iters user asked for?
        if (early_stops.iterations != False and early_stops.iterations == h):
            print("We stopped before doing iteration number: ", h)
            break
        
        # Hard stop criteria: met the threshold of unmatched items to stop?
        if (early_stops.un_t_frac != False or early_stops.un_c_frac != False):
            unmatched_treated = df_unmatched[treatment_column_name].sum()
            unmatched_control = len(df_unmatched) - unmatched_treated
            if (early_stops.un_t_frac != False and \
                unmatched_treated/tot_treated < early_stops.un_t_frac):
                print("We stopped the algorithm when ",
                      unmatched_treated/tot_treated, "of the treated units \
                      remained unmatched")
                break
            elif (early_stops.un_c_frac != False and \
                unmatched_control/tot_control < early_stops.un_c_frac):
                print("We stopped the algorithm when ",
                      unmatched_control/tot_control, "of the control units \
                      remained unmatched")
                break
        
                
        # quit if there are no more covariate sets to choose from
        if (len(consider_dropping) == 0):
            print("No more covariate sets to consider dropping")
            break
        
        # We find curr_covar_set, the best covariate to drop. 
        
        new_drop, pe = decide_drop(all_covs, consider_dropping, prev_dropped, 
                                     df_all, 
                                     treatment_column_name, outcome_column_name,
                                     df_holdout_array, adaptive_weights, weights,
                                     alpha)
        # Check for error in above step:
        if (new_drop == False):
            break
        
        return_pe.append(pe)
                
        covs_match_on = list(set(all_covs)-set(new_drop)-prev_dropped)
        matched_rows, return_matches = grouped_mr.algo2_GroupedMR(df_all, df_unmatched, 
                                                     covs_match_on, all_covs,
                                                     treatment_column_name, 
                                                     outcome_column_name,
                                                     return_matches, start_time)
        
        if (want_bf == True or early_stops.bf != False):
            # compute balancing factor
            mg_treated = matched_rows[treatment_column_name].sum()
            mg_control = len(matched_rows) - mg_treated
            available_treated = df_unmatched[treatment_column_name].sum()
            available_control = len(df_unmatched) - available_treated
            bf = mg_treated/available_treated + mg_control/available_control
            return_bf.append(bf)
            
            if bf < early_stops.bf:
                print("We stopped matching with a balancing factor of ", bf)
                break
        
        # Update covariate groups for future iterations
        consider_dropping = consider_dropping.difference([new_drop]) 
        prev_dropped.add(new_drop)
        
        # Remove matches.
        df_unmatched = df_unmatched.drop(matched_rows.index, errors='ignore')
        
        if repeats == False:
            df_all = df_unmatched

        h += 1
        
        # End of iter. Prints output based on verbose. 
        if verbose == 1:
            print("Iteration number: ", h)
        if ((verbose == 2 and (h%10==0)) or verbose == 3):
            print("Iteration number: ", h)
            if (early_stops.un_t_frac == False and early_stops.un_c_frac == False):
                unmatched_treated = df_unmatched[treatment_column_name].sum()
                unmatched_control = len(df_unmatched) - unmatched_treated
            print("Unmatched treated units: ", unmatched_treated)
            print("Unmatched control units: ", unmatched_control)
            print("Predictive error of covariates chosen this iteration: ", pe)
            if want_bf == True:
                print("Balancing Factor of this iteration: ", bf)
       
        # Do we switch to DAME?
        if (pre_dame != False and pre_dame <= h):
            
            # drop the columns that have already been matched on
            for i in prev_dropped:
                df_all = df_all.loc[:, df_all.columns.drop(i)]
                df_holdout = df_holdout.loc[:, df_holdout.columns.drop(i)]
            
            
            # call dame algorithm
            print("Moving to DAME algorithm")
            return_matches_dame = dame_algorithm.algo1(df_all, treatment_column_name, 
                                                       weights,outcome_column_name, 
                                                       adaptive_weights, alpha,
                                                       df_holdout, 
                                                       repeats, want_pe, 
                                                       verbose, want_bf,
                                                       missing_holdout_replace,
                                                       early_stops)
            # when dame is done, we
            # return the matches we made here, plus the matches made in dame.
            
            # but first, make sure anything not matched isn't in the df:
            return_matches = return_matches.dropna(axis=0) #drop rows with nan
            return_package = [return_matches, return_matches_dame]
            if want_pe == True:
                return_package.append(return_pe)
            if want_bf == True:
                return_package.append(return_bf)
            return return_package
        
        # end loop.
    return_matches = return_matches.dropna(axis=0) #drop rows with nan
    return_package = [return_matches]
    if want_pe == True:
        return_package.append(return_pe)
    if want_bf == True:
        return_package.append(return_bf)
        
    return return_package
