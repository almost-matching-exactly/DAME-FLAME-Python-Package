# -*- coding: utf-8 -*-
"""
@author: Neha

This file implements Algorithm 1 in the paper.
"""

import numpy as np
import pandas as pd
import itertools
import grouped_mr
import generate_new_active_sets
from sklearn.linear_model import Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error

def decide_drop(all_covs, active_covar_sets, weights, adaptive_weights, df,
                treatment_column_name, outcome_column_name, df_holdout):
    """ This is a helper function to Algorithm 1 in the paper. 
    
    Args:
        all_covs: This is an array of just the cov column names. 
            Not including treat/outcome
        active_covar_sets: A set of frozensets, representing all the active covar sets
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
        # We iterate
        # through all active covariate sets and find the total weight of each 
        # For each possible covariate set, temp_weight counts 
        # the total weight of the covs that are going to get used in the match,
        # or the ones *not* in that  possible cov set. 
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
            
            # error check. If this is true, we stop matching. 
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
                curr_covar_set = s
    
    return curr_covar_set, best_pe


def algo1(df_all, treatment_column_name = "T", weights = [],
          outcome_column_name = "outcome", adaptive_weights=False,
          df_holdout="", repeats=True, want_pe=False):
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
        adaptive_weights: Provided by the user, this is true if decide to drop 
            weights based on a ridge regression on hold-out training set
            or false (default) if decide to drop weights
            based on the weights given in the weight_array
        df_holdout: The cleaned, user-provided dataframe with all rows/columns. 
            There are no changes made to this throughout the code. Used only in
            testing/training for adaptive_weights version.
        ate: Bool, whether to output the ATE value for the matches.
        repeats (bool): Provided by user, whether or not values for whom a MMG 
            has been found can be used again and placed in an auxiliary group.
        want_pe (bool): Whether or not we want predictive error of each match

    Returns:
        return_matches: df of units with the column values of their main matched
            group, with "*"s in place for the columns not in their MMG
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
                  
    # Initialize return values
    if want_pe == True:
        return_pe = []
    return_matches = pd.DataFrame(columns=all_covs)
    
    # As an initial step, we attempt to match on all covariates
    
    covs_match_on = all_covs
    matched_rows, return_matches = grouped_mr.algo2_GroupedMR(
            df_all, df_all, covs_match_on, all_covs, treatment_column_name, 
            outcome_column_name, return_matches)
    
    
    # Now remove the matched units
    df_unmatched.drop(matched_rows.index, inplace=True)
    
    if repeats == False:
        df_all = df_unmatched
    
    # Here we initializing variables for the iterative portion of the code.
    # active_covar_sets indicates the sets elibible to be dropped. In the
    # paper, this is lambda_h. curr_covar_sets is the covariates chosen to be
    # dropped. In the paper, this is s*h. processed_covar_sets is the already 
    # processed sets from previous iterations. In the paper, it's delta_h. 
    
    active_covar_sets = set(frozenset([i]) for i in all_covs) 
    processed_covar_sets = set() 
        
    h = 1 # The iteration number
    
    # Here, we begin the iterative dropping procedure of DAME
    while True:
        # Iterates while there is at least one treatment unit to match in
                
        try:
            if (1 not in df_unmatched[treatment_column_name].values or \
                0 not in df_unmatched[treatment_column_name].values):
                print("We finished with no more units to match")
                break
        except TypeError:
            break
        
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
        
        if want_pe == True:
            return_pe.append(pe)              
        
        covs_match_on = list(set(all_covs)-curr_covar_set)
                
        matched_rows, return_matches = grouped_mr.algo2_GroupedMR(df_all, df_unmatched, 
                                                     covs_match_on, all_covs,
                                                     treatment_column_name, 
                                                     outcome_column_name,
                                                     return_matches)
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
        print("Iteration number: ", h)

        # end loop. 
    
    if want_pe == True:
        return return_matches, return_pe
    return return_matches