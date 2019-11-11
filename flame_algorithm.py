# -*- coding: utf-8 -*-
"""
@author: Neha

THIS FILE IS STILL UNDER DEVELOPMENT
"""
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error

# delete this one later:
import time

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
                  adaptive_weights, df_holdout, repeats=True, pre_dame=False, 
                  early_stop_iterations=False, early_stop_unmatched_c=False,
                  early_stop_unmatched_t=False, verbose=0, want_bf = False,
                  early_stop_bf = False):
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
    return_bf = []
                  
    # todo delete this comment later -- justupdated line
    return_matches = pd.DataFrame(columns=all_covs, index=df_all.index)
    
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
    tot_treated = df_all[treatment_column_name].sum()
    tot_control = len(df_all) - tot_treated
    
    consider_dropping = set(i for i in all_covs)
    prev_dropped = set()
    
    start_time = time.time()
    
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
        
        # Hard stop criteria: exceeded the number of iters user asked for?
        if (early_stop_iterations != False and early_stop_iterations == h):
            print("We stopped before doing iteration number: ", h)
            break
        
        # Hard stop criteria: met the threshold of unmatched items to stop?
        if (early_stop_unmatched_t != False or early_stop_unmatched_c != False):
            unmatched_treated = df_unmatched[treatment_column_name].sum()
            unmatched_control = len(df_unmatched) - unmatched_treated
            if (early_stop_unmatched_t != False and \
                unmatched_treated/tot_treated < early_stop_unmatched_t):
                print("We stopped the algorithm when ",
                      unmatched_treated/tot_treated, "of the treated units \
                      remained unmatched")
                break
            elif (early_stop_unmatched_c != False and \
                unmatched_control/tot_control < early_stop_unmatched_c):
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
                                     df_holdout, adaptive_weights)
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
        if (want_bf == True):
            # compute balancing factor
            mg_treated = matched_rows[treatment_column_name].sum()
            mg_control = len(matched_rows) - mg_treated
            available_treated = df_unmatched[treatment_column_name].sum()
            available_control = len(df_unmatched) - available_treated
            bf = mg_treated/available_treated + mg_control/available_control
            return_bf.append(bf)
            
            if bf < early_stop_bf:
                print("We stopped matching with a balancing factor of ", bf)
                break
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
            if (early_stop_unmatched_t == False and early_stop_unmatched_c == False):
                unmatched_treated = df_unmatched[treatment_column_name].sum()
                unmatched_control = len(df_unmatched) - unmatched_treated
            print("Unmatched treated units: ", unmatched_treated)
            print("Unmatched control units: ", unmatched_control)
            print("Predictive error of most this iteration: ", pe)
            if want_bf == True:
                print("Balancing Factor of this iteration: ", bf)
       
        # Do we switch to DAME?
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
