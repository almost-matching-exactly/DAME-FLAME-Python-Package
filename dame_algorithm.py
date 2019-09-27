# -*- coding: utf-8 -*-
"""
@author: Neha

This is Algorithm 1 in the paper.
"""

import numpy as np
import itertools
import grouped_mr
import generate_new_active_sets
import evaluation
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

def decide_drop(all_covs, active_covar_sets, weights, 
                                     adaptive_weights, df,
                                     treatment_column_name,
                                     outcome_column_name,
                                     df_holdout):
    """ This is a helper function to Algorithm 1 in the paper. 
    
    Args:
        all_covs: This is an array of just the cov column names. 
            Not including treat/outcome
        active_covar_sets: A set of frozensets, representing all the active covar sets
        weights: This is the weight array provided by the user
        adaptive_weights: This is the T/F provided by the user indicating
            whether to run ridge regression to decide who to drop. 
        df: The untouched dataset given by the user (df_all elsewhere)
        df_holdout: The cleaned, user-provided dataframe with all rows/columns. 
            There are no changes made to this throughout the code. Used only in
            testing/training for adaptive_weights version.
    """
    
    curr_covar_set = set()
    best_pe = 1000000000 # TODO: find a better max
    if adaptive_weights == False:
        # We iterate
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
        best_pe = max_weight
                
    else:
        # TODO: for now, test=train. Later, allow for separate training input
        
        # Iterate through all of the active_covar_sets and drop one at a time, 
        # and drop the one with the highest match quality score 
        # @Vittorio: 
        # This is where we decide who to drop, and also compute the pe 
        # value that gets outputted in the list described in readme. 
        
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
            
            # Calculate treated MSE
            clf = Ridge(alpha=0.1)
            clf.fit(X_treated, Y_treated) 
            predicted = clf.predict(X_treated)
            MSE_treated = mean_squared_error(Y_treated, predicted)
            
            # Calculate control MSE
            clf = Ridge(alpha=0.1)
            clf.fit(X_control, Y_control) 
            predicted = clf.predict(X_treated)
            MSE_control = mean_squared_error(Y_control, predicted)
        
            PE = MSE_treated + MSE_control
            
            # Use the smallest PE as the covariate set to drop.
            if PE < best_pe:
                best_pe = PE
                curr_covar_set = s
                
    return curr_covar_set, best_pe


def algo1(df_all, treatment_column_name = "T", weights = [],
          outcome_column_name = "outcome", adaptive_weights=False,
          df_holdout="", ate=False):
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
    return_pe= [] # list of predictive errors, 
                  # one for each item in return_covs_list
    
    # As an initial step, we attempt to match on all covariates
    
    covs = all_covs
    covs_max_list = all_covs_max_list
    return_covs_list.append(covs)
    
    matched_rows, return_matched_group, \
        return_matched_data, group_index = grouped_mr.algo2_GroupedMR(
            df_all, df_all, covs, treatment_column_name, outcome_column_name,
                    return_matched_group, return_matched_data, group_index)
 
    # TODO: Note that right now, the return_covs_list contains covs that we
    # attempted to find a match on, so we could possibly restrict it to just
    # the covariates that we did successfully find matches with via: 
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
    processed_covar_sets = set() 
        
    h = 1 # The iteration number
    
    # Her, we begin the iterative dropping procedure of DAME
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
        if (len(active_covar_sets) == 0):
            break
        
        # We find curr_covar_set, the best covariate set to drop. 
        curr_covar_set, pe = decide_drop(all_covs, active_covar_sets, weights, 
                                     adaptive_weights, df_all, 
                                     treatment_column_name, outcome_column_name,
                                     df_holdout)
        return_pe.append(pe)                
        
        # TODO: confirm, do we lose the column ordering in this set operation?                
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
        
        # Update the set of already processed covariate-sets. This works bc
        # processed_covar_sets is type set, but curr_covar_set is type frozenset
        processed_covar_sets.add(curr_covar_set)
        
        # Remove matches.
        df_unmatched = df_unmatched.drop(matched_rows.index, errors='ignore')

        h += 1

        # end loop. 
    
    # Calculate ATE if needed.
    if ate == True:
        ate = evaluation.calc_ate(return_covs_list, return_matched_group, 
                            return_matched_data, df_all, 
                            treatment_column_name, 
                            outcome_column_name)
        
    # return matched_groups
    return return_covs_list, return_matched_group, return_matched_data, return_pe, ate