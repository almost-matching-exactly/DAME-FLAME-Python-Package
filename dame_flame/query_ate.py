# -*- coding: utf-8 -*-
"""
Neha
"""

def find(mmg_of_unit, unit_id, df_all, treatment_col, outcome_col):
    ''' 
    This function is used to find the treatment effect of the unit_id
    
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
    
    avg_effect_untreated = 0
    
    df_mmg = df_all.loc[mmg_of_unit.index][:]
    
    df_mmg_treated = df_mmg.loc[df_mmg[treatment_col]==1]
    sum_treated = df_mmg_treated[outcome_col].sum()
    avg_effect_treated = sum_treated/len(df_mmg_treated)
    
    df_mmg_untreated = df_mmg.loc[df_mmg[treatment_col]==0]
    sum_untreated = df_mmg_untreated[outcome_col].sum()
    avg_effect_untreated = sum_untreated/len(df_mmg_untreated)
    
    return avg_effect_treated - avg_effect_untreated