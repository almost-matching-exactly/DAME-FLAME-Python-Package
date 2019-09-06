# -*- coding: utf-8 -*-
"""
@author: Neha
This is algorithm 2 in the paper.
"""

import numpy as np
import itertools
import flame_group_by

def algo2_GroupedMR(df_all, df_unmatched, covs, treatment_column_name,
                    outcome_column_name,
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
    df_all_without_outcome = df_all.drop([outcome_column_name], axis=1)
    matched_units, bi = flame_group_by.match_ng(df_all_without_outcome, covs, 
                                                covs_max_list, 
                                                treatment_column_name)
    
    # Prune step
    # TODO: confirm skipping this is ok
    
    # Find newly matched units and their main matched groups.
    
  
    # These are the rows of the ones that have been matched: 
    matched_rows = df_all.loc[matched_units, :].copy()
    
    matched_rows['b_i'] = bi
    
    # These are the unique values in the bi col. length = number of groups
    unique_matched_row_vals = np.unique(bi)
        
    for bi_val in unique_matched_row_vals:
        # list of all of the unit_numbers in a particular group
        units_in_g = matched_rows.index[matched_rows['b_i']==bi_val].tolist()
        
        # Add to the list of all of the units in groups with the 
        # (unitid, groupid) of the newly formed groups. 
        list_of_group_num = [group_index]*len(units_in_g)
        group_index += 1
        return_matched_data += list(zip(units_in_g, list_of_group_num))
        
        # Add to the list of matched_groups with the coefficient values of each
        # of the newly formed groups. 
        temp_row_in_group = matched_rows.loc[units_in_g[0]]
        group_covs = []
        list_covs = df_all.columns.drop(treatment_column_name).drop(outcome_column_name)
        for col in list(list_covs):
            if col in covs:
                group_covs.append(temp_row_in_group[col])
            else:
                group_covs.append('*')
        return_matched_group.append(group_covs)
        
    return matched_rows, return_matched_group, return_matched_data, group_index

