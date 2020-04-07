# -*- coding: utf-8 -*-
"""
@author: Neha Gupta, Duke University
DAME-FLAME Python Package

This file implements Algorithm 1 in the DAME paper
"""

import numpy as np
import pandas as pd
from . import grouped_mr
from . import generate_new_active_sets
from . import flame_dame_helpers



def decide_drop(all_covs, active_covar_sets, weights, adaptive_weights, df,
                treatment_column_name, outcome_column_name, df_holdout, 
                alpha_given):
    """ This is a helper function to Algorithm 1 in the paper. 
    
    Args:
        all_covs: This is an array of just the cov column names. 
            Not including treat/outcome
        active_covar_sets: A set of frozensets, representing all the active 
            covar sets
        weights: This is the weight array provided by the user
        adaptive_weights: This is the T/F provided by the user indicating
            whether to run ridge regression to decide who to drop.
        df: The untouched dataset given by the user (df_all in algo1)
        treatment_column_name (str): name of treatment column in df
        outcome_column_name (str): name of outcome column in df
        df_holdout: The cleaned, user-provided dataframe with all rows/columns. 
            There are no changes made to this throughout the code. Used only in
            testing/training for adaptive_weights version.
    """
    curr_covar_set = set()
    best_pe = 1000000000
    if adaptive_weights == False:
        # We iterate through all active covariate sets and find the total 
        # weight of each . For each possible covariate set, temp_weight counts 
        # the total weight of the covs that are going to get used in the match,
        # or the ones *not* in that possible cov set. 
        max_weight = 0
        for s in active_covar_sets: # s is a set to consider dropping
            temp_weight = 0
            for cov_index in range(len(all_covs)):  # iter through all covars
                if all_covs[cov_index] not in s:    
                    # if an item not in s, add weight. finding impact of drop s
                    temp_weight += weights[cov_index]
            if temp_weight >= max_weight:
                max_weight = temp_weight
                curr_covar_set = s # This is the items we will drop, that will
                # not get used in the match. 
        best_pe = max_weight
                
    else:
        # Iterate through all of the active_covar_sets and drop one at a time, 
        # and drop the one with the highest match quality score 
        for s in active_covar_sets:
            # S is the frozenset of covars we drop. We try dropping each one
            PE = flame_dame_helpers.find_pe_for_covar_set(df_holdout, 
                    treatment_column_name, outcome_column_name, s, 
                    adaptive_weights, alpha_given)
            # error check. PE can be float(0), but not denote error
            if PE == False and type(PE) == bool:
                return False, False
            
            # Use the smallest PE as the covariate set to drop.
            if PE < best_pe:
                best_pe = PE
                curr_covar_set = s
    
    return curr_covar_set, best_pe


def algo1(df_all, treatment_column_name = "T", weight_array = [],
          outcome_column_name = "outcome", adaptive_weights=False, alpha = 0.1,
          df_holdout="", repeats=True, want_pe=False, verbose=0,
          want_bf=False, missing_holdout_replace=False, early_stops=False):
    """This function does Algorithm 1 in the paper.

    Args:
        df_all: The cleaned, user-provided dataframe with all rows/columns. 
            There are no changes made to this throughout the code. In the 
            paper, it's called 'D'.
        treatment_column_name: As provided by the user, this indicates the name
            of the column that contains the binary indicator for whether each
            row is a treatment group or not.
        weight_array: As provided by the user, array of weights of all covariates 
            that are in df_all.
        outcome_column_name: As provided by the user, this indicates the name
            of the column that contains the outcome values. 
        adaptive_weights: Provided by the user, this is true if decide to drop 
            weights based on a ridge regression on hold-out training set
            or false (default) if decide to drop weights
            based on the weights given in the weight_array
        alpha (float): for ridge regression.
        df_holdout: The cleaned, user-provided dataframe with all rows/columns. 
            There are no changes made to this throughout the code. Used only in
            testing/training for adaptive_weights version.
        repeats (bool): Provided by user, whether or not values for whom a MMG 
            has been found can be used again and placed in an auxiliary group.
        want_pe (bool): Whether or not we want predictive error of each match
        want_bf (bool): Whether to compute and output the balancing factor of 
            each group. 
        missing_holdout_replace (bool/float): Default false. If int, the number of
            imputations that MICE needs to do on the holdout dataset, which
            has NaNs in it that need to be replaced.
        early_stops (type EarlyStop): This is all of the possible stop criteria

    Returns:
        return_matches: df of units with the column values of their main 
            matched group, with "*"s in place for the columns not in their MMG
    """
        
    # Initialize variables. These are all moving/temporary throughout algo
    all_covs = df_all.columns.tolist()
    all_covs.remove(treatment_column_name) # This is J in the paper
    all_covs.remove(outcome_column_name)
    df_unmatched = df_all.copy(deep=True) # This is df_h in the paper    
    all_covs_max_list = [max(df_all[x])+1 for x in all_covs] 
                      
    # Initialize return values
    return_pe = []
    return_bf = []
    
    return_matches = pd.DataFrame(columns=all_covs, index=df_all.index)
    
    # As an initial step, we attempt to match on all covariates
    
    covs_match_on = all_covs
    matched_rows, return_matches = grouped_mr.algo2_GroupedMR(
        df_all, df_all, covs_match_on, all_covs, treatment_column_name, 
        outcome_column_name, return_matches)
    
    
    # Now remove the matched units
    df_unmatched.drop(matched_rows.index, inplace=True)
    
    if repeats == False:
        df_all = df_unmatched
        
    # set up all the extra dfs if needed
    if missing_holdout_replace != False:
        # now df_holdout is actually an array of imputed datasets
        df_holdout = flame_dame_helpers.create_mice_dfs(
            df_holdout, missing_holdout_replace)
    else:
        # df_holdout is type array regardless, just size 1 and equal to itself
        # if not doing mice. 
        x = list()
        x.append(df_holdout)
        df_holdout = x
    # Here we initializing variables for the iterative portion of the code.
    # active_covar_sets indicates the sets elibible to be dropped. In the
    # paper, this is lambda_h. curr_covar_sets is the covariates chosen to be
    # dropped. In the paper, this is s*h. processed_covar_sets is the already 
    # processed sets from previous iterations. In the paper, it's delta_h. 
    
    active_covar_sets = set(frozenset([i]) for i in all_covs) 
    processed_covar_sets = set() 
        
    h = 1 # The iteration number
    tot_treated = df_all[treatment_column_name].sum()
    tot_control = len(df_all) - tot_treated
    prev_iter_num_unmatched = len(df_unmatched) # this is for output progress
    
    # Here, we begin the iterative dropping procedure of DAME
    while True:
        
        # Iterates until there are no more units to mach on. 
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
        
        if len(df_unmatched) == 0:
            print("All units have been matched")
            break
        
        # Hard stop criteria: exceeded the number of iters user asked for?
        if (early_stops.iterations != False and early_stops.iterations == h):
            print((len(df_all) - len(df_unmatched)), "units matched. "\
                  "We stopped before doing iteration number: ", h)
            break
        
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
            if (early_stops.un_c_frac != False and \
                unmatched_control/tot_control < early_stops.un_c_frac):
                print("We stopped the algorithm when ",
                      unmatched_control/tot_control, "of the control units "\
                      "remained unmatched")
                break
        
        # quit if there are covariate sets to choose from
        if (len(active_covar_sets) == 0):
            print((len(df_all) - len(df_unmatched)), "units matched. "\
                "We stopped after considering all covariate set options")
            break
        
        # We find curr_covar_set, the best covariate set to drop. 
        curr_covar_set, pe = decide_drop(
            all_covs, active_covar_sets, weight_array, adaptive_weights, 
            df_all, treatment_column_name, outcome_column_name, df_holdout, 
            alpha)
        
        # Check for error in above step:
        if (curr_covar_set == False):
            print((len(df_all) - len(df_unmatched)), "units matched. "\
                  "We stopped when the holdout set was not large enough or "\
                  "there was nothing left to match")
            break
        
        return_pe.append(pe)              
        
        covs_match_on = list(set(all_covs)-curr_covar_set)
                
        matched_rows, return_matches = grouped_mr.algo2_GroupedMR(
           df_all, df_unmatched, covs_match_on, all_covs,
           treatment_column_name, outcome_column_name, return_matches)
        
        # It's probably slow to compute this if people don't want it, so will
        # want to add this, I think. 
        if (want_bf == True or early_stops.bf != False):
            # compute balancing factor
            mg_treated = matched_rows[treatment_column_name].sum()
            mg_control = len(matched_rows) - mg_treated
            available_treated = df_unmatched[treatment_column_name].sum()
            available_control = len(df_unmatched) - available_treated
            if (available_treated != 0 and available_control != 0):
                bf = mg_treated/available_treated + mg_control/available_control
            else:
                bf = np.nan
            return_bf.append(bf)
            
            if (bf < early_stops.bf):
                print((len(df_all) - len(df_unmatched)), "units matched. "\
                        "We stopped matching with a balancing factor of ", bf)
                break
        
        if (early_stops.pe != False):
            if pe <= early_stops.pe:
                print((len(df_all) - len(df_unmatched)), "units matched. "\
                        "We stopped matching with a pe of ", pe)
                break
            
            
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
        # End of iter. Decide what to print to user depending on verbose var. 
        if verbose == 1:
            print("Iteration number: ", h)
        if ((verbose == 2 and (h%10==0)) or verbose == 3):
            print("Iteration number: ", h)
            if (early_stops.un_t_frac == False and early_stops.un_c_frac == False):
                unmatched_treated = df_unmatched[treatment_column_name].sum()
                unmatched_control = len(df_unmatched) - unmatched_treated
            total_treated = df_all[treatment_column_name].sum()
            print("Unmatched treated units: ", unmatched_treated,
                  "out of a total of ", total_treated, "treated units .")
            print("Unmatched control units: ", unmatched_control,
                  "out of a total of ", len(df_all)-total_treated, 
                  "control units")
            print("Predictive error of covariates chosen this iteration: ", pe)
            print("Number of matches made in this iteration: ", 
                  prev_iter_num_unmatched - len(df_unmatched))
            print("Number of matches made so far: ", len(df_all) - len(df_unmatched))
            print("In this iteration, the covariates dropped are: ", curr_covar_set)
            if want_bf == True:
                print("Balancing factor of this iteration: ", bf)
                
            prev_iter_num_unmatched = len(df_unmatched)
        
    # end loop. 
    return_matches = return_matches.dropna(axis=0) # drop rows with nan, dont return unmatched stuff
    return_package = [return_matches]
    if want_pe == True:
        return_package.append(return_pe)
    if want_bf == True:
        return_package.append(return_bf)
        
    return return_package