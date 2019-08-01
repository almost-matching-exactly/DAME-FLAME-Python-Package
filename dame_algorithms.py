# -*- coding: utf-8 -*-

import itertools
import flame_group_by


def algo1(df_all, treatment_column_name = "T", weights = []):
    """This function does Algorithm 1 in the paper.

    Args:
        D: The data. 

    Returns:
        MG: Matched groups from all iterations. 

    """
    
    # Initialize variables
    matched_groups = [] #This is a list of lists
    all_covs = df_all.columns.tolist()
    all_covs.remove(treatment_column_name) # This is J in the paper. 
    df_h = df_all.copy(deep=True) # df_all will be the original D in the paper, unedited.
                  # df_h will be the one that gets edited by dropping matches
    
    # This is the max of all of the columns. For now, I'm assuming they're 
    # ordered from least to greatest. 
    all_covs_max_list = [max(df_all[x])+1 for x in all_covs]
    
    # Do the first match on all of the variables. Initial step. 
    covs = all_covs
    covs_max_list = all_covs_max_list
    matched_units, bi = flame_group_by.match_ng(df_all, covs, covs_max_list, treatment_column_name)
    # Now remove the matched units:
    
    # These are the rows of the ones that have been matched: 
    matched_rows = df_h.loc[matched_units, :].copy()
    
    # To add those matched rows as pairs in matched_groups.
    matched_rows['b_i'] = bi
    matched_groups.append(matched_rows)
    
    # To drop those indexes:
    df_h.drop(matched_rows.index, inplace=True)
    
    #print("df_h", df_h)
    #print("matched_groups", matched_groups[0])
    # print()
    
    # Initializing stuff for the iterative portion of the code. 
    lambda_h = set(frozenset([i]) for i in all_covs) # This is the array of 
                                                     # active covariate sets
                                                     # eligible to be dropped
    s_star_h = [] # the covariates you're dropping in iteration h
    delta_h = set() # The covariates at iteration h that have been processed
    h = 1 # The iteration number
    
    # Do the iterative dropping procedure of DAME
    while True:
        # Do while there is at least one treatment unit to match in
        try:
            if (1 not in df_h[treatment_column_name].values):
                break
        except TypeError:
            break
        
        # Find s_star_h, the max of theta*w
        max_weight = 0
        for s in lambda_h: 
            # TODO: come back and optimize this. I think it'll be slow. 
            temp_weight = 0
            #theta-t-s = 
            #theta_times_weight = 
            for cov_index in range(len(all_covs)):
                if all_covs[cov_index] not in s:
                    temp_weight += weights[cov_index]
            if temp_weight >= max_weight:
                max_weight = temp_weight
                s_star_h = s
                        
        # So now we call GroupedMR, Algorithm 2.
        # TODO: confirm, do we lose the column ordering in that set operation?
        matched_rows = algo2_GroupedMR(df_all, df_h, list(set(all_covs)-s_star_h), treatment_column_name)
        matched_groups.append([matched_rows])
                
        # Generate new active sets
        Z_h = algo3GenerateNewActiveSets(s_star_h, delta_h)
        
        # Remove s_star_h from the set of active sets
        delta_h = delta_h.difference(s_star_h) #TODO: is this the fastest remove?
        
        # Update the set of active sets
        lambda_h.union(Z_h)
        
        # Update the set of already processed covariate-sets
        delta_h = delta_h.union(s_star_h)
        
        # Remove matches.
        df_h = df_h.drop(matched_rows.index, inplace=True, errors='ignore')

        h += 1
        print("DF_H", df_h)
        # end loop. 
    
    return matched_groups

def algo2_GroupedMR(df_all, df_h, covs, treatment_column_name):
    # Random idea: could create a data object getting passed around with df_all
    # and treatment-column-name and possibly the least ot greatest ordering?
    '''
    Input: The dataframe of all of the data
            df_h: The dataframe ofjust hte unmatched data, a subset of df
            covs: A subset of indexes of all covariates.
    Output:The newly matched units using covs indexed by Js.
    '''
    
    # This is the max of all of the columns. assuming they're 
    # ordered from least to greatest. 
    # If we lost column ordering in the todo above, this would go wrong:
    covs_max_list = [max(df_h[x])+1 for x in covs]
    
    # Form groups on D by exact matching on Js.  
    matched_units, bi = flame_group_by.match_ng(df_all, covs, covs_max_list, treatment_column_name)
    
    # Prune step
    # TODO: confirm skipping this is ok
    
    # Find newly matched units and their main matched groups.
    
  
    # These are the rows of the ones that have been matched: 
    matched_rows = df_all.loc[matched_units, :].copy()
    
    # To add those matched rows as pairs in matched_groups.
    matched_rows['b_i'] = bi
    #matched_groups.append([matched_rows])
    
    return matched_rows


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