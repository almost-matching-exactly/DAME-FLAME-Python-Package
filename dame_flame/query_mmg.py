# -*- coding: utf-8 -*-
"""
@author: Neha
"""

def find(match_result_df, unit_id, df_all):
    ''' 
    This function is used to find the main matched group of the unit_id
    
    Args:
        match_result_df: The algorithm's pre-calculated dataframe with all 
            the groups of each unit
        unit_id: the id of the unit that we want to match
        df_all: The cleaned, user-provided dataframe with all rows/columns. 
            There are no changes made to this throughout the code. In the 
            paper, it's called 'D'.

    Returns:
        mmg_matches: the subset of df_all with only units that in the mmg
    '''
    if (len(match_result_df.columns) == 0 or len(match_result_df) == 0):
        return False
    
    if unit_id not in match_result_df.index:
        return False
    
    # Pandas series object which is all of the covariates of that unit (with *)
    group_of_unit = match_result_df.loc[unit_id]
    
    # we want to get all the rows in df_all that have the same covariates as
    # unit_id. Unfortunately, it appears that python doesn't support querying multiple
    # rows at a time unless you know that the colnames fit requirements. 
    mmg_matches = df_all[match_result_df.columns]
    for colname,group_val in group_of_unit.iteritems():
        # We only care if they match if it's not a '*'
        if group_val == "*":
            continue
        else:
            mmg_matches = mmg_matches.loc[mmg_matches[colname] == group_val]
            
    return mmg_matches
            
    
    