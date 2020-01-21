# -*- coding: utf-8 -*-
"""
@author: Neha
This is algorithm 2 in the paper.
"""

import numpy as np
from . import flame_group_by

def algo2_GroupedMR(df_all, df_unmatched, covs_match_on, all_covs, treatment_column_name,
                    outcome_column_name, return_groups, start_time=0):    
    # todo; DOn't forget to remove start_time!
    ''' 
    Input: 
        df_all: The dataframe of all of the data
            df_unmatched: The dataframe ofjust hte unmatched data, a subset of df
            covs_match_on (array): List of strs with name of columns of df. 
                            A subset of indexes of all covariates.
            all_covs (array): list of all covariates. 
    Output: 
        matched_rows: newly matched units using covs indexed by Js. Type df
        return_groups: The df of unit id and covar values matched on, with '*"
            for the irrelevant ones. 
    
    '''
    
    # This is the max of all of the columns. assuming they're 
    # ordered from least to greatest. 
    covs_max_list = [max(df_unmatched[x])+1 for x in covs_match_on]
    # Form groups on D by exact matching on Js.  
    df_all_without_outcome = df_all.drop([outcome_column_name], axis=1)
    matched_units, bi = flame_group_by.match_ng(df_all_without_outcome, covs_match_on, 
                                                covs_max_list, 
                                                treatment_column_name)

    # Find newly matched units and their main matched groups.
    
  
    # These are the rows of the ones that have been matched: 
    matched_rows = df_all.loc[matched_units, :].copy()
    matched_rows['b_i'] = bi
            
    # These are the unique values in the bi col. length = number of groups
    unique_matched_row_vals = np.unique(bi)
        
    for bi_val in unique_matched_row_vals:
        # type "int64index", ~ list, all of the unit_numbers in a matched group.
        units_in_g = matched_rows.index[matched_rows['b_i']==bi_val]
        
        # Which of the units of this new group haven't been matched yet? 
        # unique_matched is a subset of units in the matched group, just the
        # ones for whom this is their main matched group. 
                
        newly_matched = [i for i in units_in_g if i in df_unmatched.index]
        # Only need to proceed to fill in the return table if someone's MMG found. 
        if len(newly_matched) != 0:
            # What does the group look like? eg [1,2,*,1]
            temp_row_in_group = matched_rows.loc[units_in_g[0]] 
            # ^ that line arbitrarily chooses the first row that has the bi_val so
            # the first row of that group. 
            group_covs = []
            for col in all_covs:
                if col in covs_match_on:
                    group_covs.append(temp_row_in_group[col])
                else:
                    group_covs.append('*')
            # add that group to the newly matched units to our new dataframe
           
            return_groups.loc[newly_matched,:] = group_covs
            
            # OTHER IDEA: 
            # store the bi in a column with df_all and also a column for "pair" with another
            # persons unit id. 
            # don't update that when someone gets added to an auxiliary matched group
            # then at the end, iterate through it and create the nicely formatteed output. 
        
    return matched_rows, return_groups