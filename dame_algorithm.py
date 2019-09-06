# -*- coding: utf-8 -*-
"""
@author: Neha

This is Algorithm 1 in the paper.
"""

import numpy as np
import itertools
import grouped_mr
import generate_new_active_sets


def algo1(df_all, treatment_column_name = "T", weights = [],
          outcome_column_name = "outcome"):
    """This function does Algorithm 1 in the paper.

    Args:
        df_all: The cleaned, user-provided dataframe with all rows/columns. 
            There are no changes made to this throughout the code. In the 
            paper, it's called 'D'.
        treatment_column_name: As provided by the user, this indicates the name
            of the column that contains the binary indicator for whether each
            row is a treatment group or not.
        weights: As provided by the user, array of weights of all covariates 
            that are in df_all.
        outcome_column_name: As provided by the user, this indicates the name
            of the column that contains the outcome values. 

    Returns:
        return_covs_list: List of lists, indicates which covariates were used 
            in each match. So first element is a list of covariates used in the
            first match.
        return_matched_group: List of lists, indicates what values were used
            in each group. So first element is a list of values each covariate
            had in the first group.
        return_matched_data: List of tuples (unit num, group num). indicates 
            what unit numbers belong to what group numbers.
    """
    # Initialize variables. These are all moving/temporary throughout algo
    matched_groups = [] # This is a list of df's. Will be replaced for new output.
    all_covs = df_all.columns.tolist()
    all_covs.remove(treatment_column_name) # This is J in the paper
    all_covs.remove(outcome_column_name)
    df_unmatched = df_all.copy(deep=True) # This is df_h in the paper    
    all_covs_max_list = [max(df_all[x])+1 for x in all_covs] 
    
    # Indexes the group numbers throughout. 
    group_index = 0
    
    # The items getting returned
    return_covs_list = [] # each index is that iteration's cov list matched on
    return_matched_group = [] # gid & covar list
    return_matched_data = [] # uid and gid list. 
    
    # As an initial step, match on all covariates
    
    covs = all_covs
    covs_max_list = all_covs_max_list
    return_covs_list.append(covs)
    
    matched_rows, return_matched_group, \
        return_matched_data, group_index = grouped_mr.algo2_GroupedMR(
            df_all, df_all, covs, treatment_column_name, outcome_column_name,
                    return_matched_group, return_matched_data, group_index)
 
    # TODO: is this how we want it, or do we want the above?
    #if (len(matched_rows) != 0):
        # only if we found a match do we add to the covs list
    #    return_covs_list.append(covs)
    
    # Now remove the matched units
    df_unmatched.drop(matched_rows.index, inplace=True)
    
    # Here we initializing variables for the iterative portion of the code.
    # active_covar_sets indicates the sets elibible to be dropped. In the
    # paper, this is lambda_h. curr_covar_sets is the covariates chosen to be
    # dropped. In the paper, this is s*h. processed_covar_sets is the already 
    # processed sets from previous iterations. In the paper, it's delta_h. 
    
    active_covar_sets = set(frozenset([i]) for i in all_covs) 
    curr_covar_set = set()
    processed_covar_sets = set() 
        
    h = 1 # The iteration number
    
    # This is the iterative dropping procedure of DAME
    while True:
        # Iterates while there is at least one treatment unit to match in
        # TODO: shouldn't there also be at least one control unit to match in?
        try:
            if (1 not in df_unmatched[treatment_column_name].values):
                break
        except TypeError:
            break
        
        # TODO: Also add early stopping critera based on low match quality.
        
        # We find curr_covar_set, the best covariate set to drop. We iterate
        # through all active covariate sets and find the total weight of each 
        # For each possible covariate set, temp_weight counts 
        # the total weight of the covs that are going to get used in the match,
        # or the ones *not* in that  possible cov set. 
        # TODO: come back and make it more readable/optimize?

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
                        
        # So now we call GroupedMR, Algorithm 2.
        # TODO: confirm, do we lose the column ordering in this set operation?

        # the paper asks that theta has 1 if covar not in s, and calls 
        # groupedMR on j - s and I accidentally reversed it. 
        
        
        covs_match_on = list(set(all_covs)-curr_covar_set)
        # covs_match_on = list(set(curr_covar_set))
        
        return_covs_list.append(covs_match_on)
        matched_rows, return_matched_group, return_matched_data, \
            group_index = grouped_mr.algo2_GroupedMR(df_all, df_unmatched, 
                                                     covs_match_on, 
                                                     treatment_column_name, 
                                                     outcome_column_name,
                                                     return_matched_group,
                                                     return_matched_data, 
                                                     group_index)
               
        # Generate new active sets
        Z_h = generate_new_active_sets.algo3GenerateNewActiveSets(
                curr_covar_set, processed_covar_sets)
        
        # Remove curr_covar_set from the set of active sets
        active_covar_sets = active_covar_sets.difference([curr_covar_set]) 

        # Update the set of active sets
        active_covar_sets = active_covar_sets.union(Z_h)
        
        # Update the set of already processed covariate-sets
        processed_covar_sets = processed_covar_sets.union(curr_covar_set)
                
        # Remove matches.
        df_unmatched = df_unmatched.drop(matched_rows.index, errors='ignore')

        h += 1

        # end loop. 
    
    # return matched_groups
    return return_covs_list, return_matched_group, return_matched_data