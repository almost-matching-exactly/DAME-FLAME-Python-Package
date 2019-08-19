# -*- coding: utf-8 -*-

import numpy as np
import itertools
import flame_group_by


def algo1(df_all, treatment_column_name = "T", weights = []):
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

    Returns:
        MG: Matched groups from all iterations. This is going to change.

    """
    
    # Initialize variables. These are all moving/temporary throughout algo
    matched_groups = [] # This is a list of df's. Will be replaced for new output.
    all_covs = df_all.columns.tolist()
    all_covs.remove(treatment_column_name) # This is J in the paper
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
    
    matched_rows, return_matched_group, return_matched_data, group_index = algo2_GroupedMR(
            df_all, df_all, covs, treatment_column_name,
                    return_matched_group, return_matched_data, group_index)
 
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
        try:
            if (1 not in df_unmatched[treatment_column_name].values):
                break
        except TypeError:
            break
        
        # We find curr_covar_set, the best covariate set to drop. We iterate
        # through all active covariate sets and find the total weight of each 
        # For each possible covariate set, temp_weight counts 
        # the total weight of the covs that are going to get used in the match,
        # or the ones *not* in that  possible cov set. 
        # TODO: come back and optimize this. I think it could be better.

        max_weight = 0
        for s in active_covar_sets: # s is a set to consider dropping
            temp_weight = 0
            for cov_index in range(len(all_covs)):  # cov_index is a 
                if all_covs[cov_index] not in s:    
                    temp_weight += weights[cov_index]
            if temp_weight >= max_weight:
                max_weight = temp_weight
                curr_covar_set = s
                        
        # So now we call GroupedMR, Algorithm 2.
        # TODO: confirm, do we lose the column ordering in this set operation?
        covs_match_on = list(set(all_covs)-curr_covar_set)
        return_covs_list.append(covs_match_on)
        matched_rows, return_matched_group, return_matched_data, group_index = algo2_GroupedMR(df_all, df_unmatched, covs_match_on, 
                                       treatment_column_name, 
                                       return_matched_group,
                                       return_matched_data, group_index)
               
        # Generate new active sets
        Z_h = algo3GenerateNewActiveSets(curr_covar_set, processed_covar_sets)
        
        # Remove curr_covar_set from the set of active sets
        # TODO: is this the fastest remove?
        processed_covar_sets = processed_covar_sets.difference(curr_covar_set) 
        
        # Update the set of active sets
        active_covar_sets.union(Z_h)
        
        # Update the set of already processed covariate-sets
        processed_covar_sets = processed_covar_sets.union(curr_covar_set)
        
        # Remove matches.
        df_unmatched = df_unmatched.drop(matched_rows.index, inplace=True, 
                                         errors='ignore')

        h += 1

        # end loop. 
    
    # return matched_groups
    return return_covs_list, return_matched_group, return_matched_data

def algo2_GroupedMR(df_all, df_unmatched, covs, treatment_column_name,
                    return_matched_group, return_matched_data, group_index):
    # Random idea: could create a data object getting passed around with df_all
    # and treatment-column-name and possibly the least ot greatest ordering?
    '''
    Input: The dataframe of all of the data
            df_unmatched: The dataframe ofjust hte unmatched data, a subset of df
            covs (array): List of strs with name of columns of df. 
                            A subset of indexes of all covariates.
    Output: matched_rows: newly matched units using covs indexed by Js. Type df
    '''
    
    # This is the max of all of the columns. assuming they're 
    # ordered from least to greatest. 
    # If we lost column ordering in the todo above, this would go wrong:
    covs_max_list = [max(df_unmatched[x])+1 for x in covs]
    
    # Form groups on D by exact matching on Js.  
    matched_units, bi = flame_group_by.match_ng(df_all, covs, covs_max_list, 
                                                treatment_column_name)
    # Prune step
    # TODO: confirm skipping this is ok
    
    # Find newly matched units and their main matched groups.
    
  
    # These are the rows of the ones that have been matched: 
    matched_rows = df_all.loc[matched_units, :].copy()
    
    matched_rows['b_i'] = bi
    not_covs = list(set(df_all.columns) - set(covs) - set('T'))
    
    # These are the unique values in the bi col. length = number of groups
    unique_matched_row_vals = np.unique(bi)
        
    for bi_val in unique_matched_row_vals:
        # list of all of the items in a particular group
        units_in_g = matched_rows.index[matched_rows['b_i']==bi_val].tolist()
        list_of_group_num = [group_index]*len(units_in_g)
        group_index += 1
        return_matched_data += list(zip(units_in_g, list_of_group_num))
        
        temp_row_in_group = matched_rows.loc[units_in_g[0]]
        group_covs = []
        for col in list(df_all.columns):
            if col in covs:
                group_covs.append(temp_row_in_group[col])
            else:
                group_covs.append('*')
        return_matched_group.append(group_covs)
        
    return matched_rows, return_matched_group, return_matched_data, group_index


#TODO: split steps into separate tiny functions for more unittests
#TODO: validate function input.
def algo3GenerateNewActiveSets(s, delta):
    """This function does Algorithm 3 in the paper.

    Args:
        s: A newly dropped set of size k. Stored as a set with 1 tuple of ints. 
        delta: the set of previously processed sets. Previously processed sets 
        are all stored as tuble objects, so this is a set of tuples.

    Returns:
        Z, the new active sets. Stored as set of sets.

    """
    # TODO: explore variable names
    
    Z = set()
    k = len(list(s)[0])
    set_s = set(list(s)[0])
    
    # Step 3: delta_k is all subsets of delta that are size k, and s. 
    subsets_size_k = set()
    for prev_processed_tup in delta:
        if len(prev_processed_tup) == k:
            subsets_size_k.add(prev_processed_tup)
    delta_k = subsets_size_k.union(s)
        
    # Step 4: rho is all the covariates contained in sets in delta_k
    rho = set()
    for tup in delta_k:
        for i in tup:
            rho.add(i)
                
    # Step 5: s_e is the support of covariate e in delta_k, for covars in rho
    # TODO: combine this with above loop, calculating rho, for time efficiency.
    s_e = dict()
    for e in rho:
        s_e[e] = 0
        for tup in delta_k:
            if e in tup:
                s_e[e] += 1
                    
    # Step 6: omega is all the covariates not in s that have enough support
    dict_covars_eno = dict((key, val) for key, val in s_e.items() if val >= k) 
    omega = set(dict_covars_eno.keys())
    omega = omega.difference(set_s)
    
       
    # Step 7: do all covariates in S have enough support in delta_k?
    # TODO: confirm this step is right. 
    for e,support_e in s_e.items():
        if e in s and support_e < k:
            return Z
        
    # Step 8
    for alpha in omega:
        # Step 9
        r = set_s.union(set([alpha]))
        
        # Step 10: Get all subsets of size k in r, check if belong in delta_k
        
        # Have to convert these to sets and frozen sets before doing the search
        delta_k = set(frozenset(i) for i in delta_k)
        subsets_size_k = set(list(itertools.combinations(r, k)))
        subsets_size_k = set(frozenset(i) for i in subsets_size_k)
        #subset = set(subset)
        allin = True
        for subset in subsets_size_k:
            if subset not in delta_k:
                allin = False
                break
            
        if allin == True:
            # Step 11: Add r to Z
            Z.add(frozenset(r))
    
    return Z