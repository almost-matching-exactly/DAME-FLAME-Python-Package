# -*- coding: utf-8 -*-
"""
@author: Neha
"""
import pandas as pd

from . import grouped_mr
from . import dame_algorithm
from . import flame_dame_helpers

def decide_drop(all_covs, consider_dropping, prev_drop, df_all, 
                treatment_column_name, outcome_column_name, df_holdout_array, 
                adaptive_weights, alpha_given, df_unmatched, return_matches, 
                C):
    """
    This is the decide drop function. 
    """
    
    # This is where we decide who to drop, and also compute the pe 
    # value that gets outputted in the list described in readme. 
    best_drop = 0
    best_mq = -100000
    best_return_matches = 0
    best_matched_rows = 0
    best_bf = 0
    
    for poss_drop in consider_dropping:
        # S is the frozenset of covars we drop. We try dropping each one
        s = prev_drop.union([poss_drop])
        
        PE = flame_dame_helpers.find_pe_for_covar_set(
            df_holdout_array, treatment_column_name, outcome_column_name, s, 
            adaptive_weights, alpha_given)
        
        # error check. PE can be float(0), but not denote error
        if PE == False and type(PE) == bool:
            return False, False, False, False, False
        
        # The dropping criteria for FLAME is max MQ
        # MQ = C * BF - PE
        
        all_covs = set(all_covs)
        covs_match_on = all_covs.difference([poss_drop]).difference(prev_drop)
        covs_match_on = list(covs_match_on)
                
        # need to make sure we don't edit the mutable dataframes, then do match
        df_all_temp = df_all.copy(deep=True)
        return_matches_temp = return_matches.copy(deep=True)
        matched_rows, return_matches_temp = grouped_mr.algo2_GroupedMR(
            df_all_temp, df_unmatched, covs_match_on, all_covs, 
            treatment_column_name, outcome_column_name, return_matches_temp)

        # find the BF for this covariate set's match. 
        BF = flame_dame_helpers.compute_bf(
            matched_rows, treatment_column_name, df_unmatched)
        
        # Use the largest MQ as the covariate set to drop.
        MQ = C * BF - PE
        if MQ > best_mq:
            best_mq = MQ
            best_pe = PE
            best_bf = BF
            best_drop = poss_drop
            best_return_matches = return_matches_temp
            best_matched_rows = matched_rows
                
    return best_drop, best_pe, best_matched_rows, best_return_matches, best_bf

def flame_generic(df_all, treatment_column_name, outcome_column_name, 
                  adaptive_weights, alpha, df_holdout, repeats, want_pe,
                  verbose, want_bf, missing_holdout_replace, early_stops,
                  pre_dame, C):
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
                  
    return_matches = pd.DataFrame(columns=all_covs, index=df_all.index)
    # As an initial step, we attempt to match on all covariates
    
    covs_match_on = all_covs
    
    matched_rows, return_matches = grouped_mr.algo2_GroupedMR(
        df_all, df_unmatched, covs_match_on, all_covs, treatment_column_name, 
        outcome_column_name, return_matches)

    # Now remove the matched units
    df_unmatched.drop(matched_rows.index, inplace=True)
        
    if repeats == False:
        df_all = df_unmatched
    
    # set up all the extra dfs if needed
    if missing_holdout_replace != False:
        # now df_holdout is actually an array of imputed datasets
        df_holdout_array = flame_dame_helpers.create_mice_dfs(
            df_holdout, missing_holdout_replace)
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
        
    # Here, we begin the iterative dropping procedure of FLAME
    while True:
        # Iterates while there are units to match to match in
        try:
            if ((early_stops.unmatched_t == True or repeats == False) and 
                (1 not in df_unmatched[treatment_column_name].values)): 
                print((len(df_all) - len(df_unmatched)), "units matched. "\
                      "We finished with no more units to match")
                break
            
            if ((early_stops.unmatched_c == True or repeats == False) and 
                (0 not in df_unmatched[treatment_column_name].values)):
                print((len(df_all) - len(df_unmatched)), "units matched. "\
                      "We finished with no more units to match")
                break
        except TypeError:
            break
        
         # Hard stop criteria: stop when there are no more units to match
        if (len(df_unmatched) == 0):
            print("All units have been matched.")
            break
        
        # Hard stop criteria: exceeded the number of iters user asked for?
        if (early_stops.iterations != False and early_stops.iterations == h):
            print((len(df_all) - len(df_unmatched)), "units matched. "\
                  "We stopped before doing iteration number: ", h)
            break
        
        
        # Hard stop criteria: met the threshold of unmatched items to stop?
        unmatched_treated = df_unmatched[treatment_column_name].sum()
        unmatched_control = len(df_unmatched) - unmatched_treated
        
        # Hard stop criteria: met the threshold of unmatched items to stop?

        if (early_stops.un_t_frac != False or early_stops.un_c_frac != False):
            unmatched_treated = df_unmatched[treatment_column_name].sum()
            unmatched_control = len(df_unmatched) - unmatched_treated
            if (early_stops.un_t_frac != False and \
                unmatched_treated/tot_treated < early_stops.un_t_frac):
                print("We stopped the algorithm when ",
                      unmatched_treated/tot_treated, "of the treated units "\
                      "remained unmatched")
                break
            elif (early_stops.un_c_frac != False and \
                unmatched_control/tot_control < early_stops.un_c_frac):
                print("We stopped the algorithm when ",
                      unmatched_control/tot_control, "of the control units "\
                      "remained unmatched")
                break
        
                
        # quit if there are no more covariate sets to choose from
        if (len(consider_dropping) == 1):
            print((len(df_all) - len(df_unmatched)), "units matched. "\
                  "No more covariate sets to consider dropping")
            break
                        
        new_drop, pe, matched_rows, return_matches, bf = decide_drop(all_covs, 
            consider_dropping, prev_dropped, df_all, treatment_column_name, 
            outcome_column_name, df_holdout_array, adaptive_weights, alpha, 
            df_unmatched, return_matches, C)
                     
        # Check for error in above step:
        if (new_drop == False):
            break
        
        return_pe.append(pe)
        
        if (want_bf == True):
            # if we need to track the bf, do so. 
            return_bf.append(bf)
            
        if (early_stops.bf != False):
            if (bf < early_stops.bf):
                print((len(df_all) - len(df_unmatched)), "units matched. "\
                      "We stopped matching with a balancing factor of ", bf)
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
            if (early_stops.un_t_frac == False and 
                early_stops.un_c_frac == False):
                unmatched_treated = df_unmatched[treatment_column_name].sum()
                unmatched_control = len(df_unmatched) - unmatched_treated
            print("Unmatched treated units: ", unmatched_treated)
            print("Unmatched control units: ", unmatched_control)
            print("Predictive error of covariates chosen this iteration: ", pe)
            print("The covariate dropped during this iteration: ", new_drop)
            if want_bf == True:
                print("Balancing Factor of this iteration: ", bf)
       
        # Do we switch to DAME?
        if (pre_dame != False and pre_dame <= h):
            
            # drop the columns that have already been matched on
            for i in prev_dropped:
                df_all = df_all.loc[:, df_all.columns.drop(i)]
                df_holdout = df_holdout.loc[:, df_holdout.columns.drop(i)]
            
            
            # call dame algorithm
            print((len(df_all) - len(df_unmatched)), "units matched. "\
                  "Moving to DAME algorithm")
            return_matches_dame = dame_algorithm.algo1(
                df_all, treatment_column_name, False, outcome_column_name, 
                adaptive_weights, alpha, df_holdout, repeats, want_pe, 
                verbose, want_bf, missing_holdout_replace, early_stops)
            
            # when dame is done, we
            # return the matches we made here, plus the matches made in dame.
            
            # but first, make sure anything not matched isn't in the df:
            return_matches = return_matches.dropna(axis=0) #drop rows with nan
            return_package = [return_matches, return_matches_dame]
            if (want_pe == True):
                return_package.append(return_pe)
            if (want_bf == True):
                return_package.append(return_bf)
            return return_package
                
        
        # end loop.
    return_matches = return_matches.dropna(axis=0) #drop rows with nan
    return_package = [return_matches]
    if (want_pe == True):
        return_package.append(return_pe)
    if (want_bf == True):
        return_package.append(return_bf)
        
    return return_package
