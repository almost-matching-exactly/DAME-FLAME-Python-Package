# -*- coding: utf-8 -*-

"""Does the bit matching algo from "Fast Large Scale..."(Wang, et al)"""

# author: Neha Gupta, Duke University
# Copyright Duke University 2020
# License: MIT

from operator import itemgetter
import numpy as np
import pandas as pd
from . import flame_group_by

def algo2_GroupedMR(df_all, df_unmatched, covs_match_on, all_covs, treatment_column_name,
                    outcome_column_name, return_groups):
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
        all_units_in_g: list of unit ids for all matched groups created

    '''
    covs_max_tuples =list(zip(list(df_all[covs_match_on].max()+1),covs_match_on))
    covs_max_tuples = sorted(covs_max_tuples, key=itemgetter(0))
    covs_max_list, covs_match_on = map(list, zip(*covs_max_tuples))
    df_all_without_outcome = df_all.drop([outcome_column_name], axis=1)
    matched_units, bi = flame_group_by.match_ng(df_all_without_outcome,
                                                covs_match_on, covs_max_list,
                                                treatment_column_name)
    matched_rows = df_all.loc[matched_units, :].copy()
    matched_rows['b_i'] = bi
    unique_matched_row_vals = np.unique(bi)
    matched_rows_temp=matched_rows.reset_index()
    # get index of matched_rows that is in df_unmatched
    matched_rows_temp['matched']=matched_rows_temp['index'].isin(df_unmatched.index)
    # group index and matched status of matched_rows by unique b_i
    # to replace 
    # if len(newly_matched) != 0:
    #     all_units_in_g.append(list(units_in_g))
    matched_rows_temp=matched_rows_temp.groupby('b_i').agg({'index': list,'matched':sum})
    all_units_in_g=matched_rows_temp[matched_rows_temp['matched']!=0]['index'].values.tolist()
    # replacing
    # if len(newly_matched) != 0:
    #     temp_row_in_group = matched_rows.loc[units_in_g[0]]
    #     group_covs = []
    #     for col in return_groups.columns:
    #         if col in covs_match_on:
    #             group_covs.append(temp_row_in_group[col])
    #         else:
    #             group_covs.append('*')
    # find first row of each match group
    if len(matched_rows_temp)==0:
        matched_rows_first=pd.DataFrame(columns=['index'])
    else:
        matched_rows_first=matched_rows_temp[matched_rows_temp['matched']!=0]['index'].str[0]
    # filter matched_rows by the first row of each match group
    matched_rows_first=matched_rows[matched_rows.index.isin(matched_rows_first.values.tolist())][return_groups.columns]
    # fill unmatched covs by *
    matched_rows_first[list(set(return_groups.columns)-set(covs_match_on))]='*'
    # join by b_i
    return_groups_copy=return_groups.join(matched_rows[['b_i']],how='left')
    
    # identify unmatched index
    return_groups_copy['unmatched']=return_groups_copy.index.isin(df_unmatched.index)
    # fill return_groups_copy if index is in matched_rows_first
    return_groups_copy.loc[matched_rows_first.index,matched_rows_first.columns]=matched_rows_first
    # forward fill return_groups_copy for each unique b_i by first rows
    return_groups_copy.loc[return_groups_copy['b_i'].notna(),matched_rows_first.columns.to_list()]=return_groups_copy.loc[return_groups_copy['b_i'].notna(),['b_i']+matched_rows_first.columns.to_list()].groupby('b_i').transform('first')
    index=return_groups_copy['b_i'].notna() & return_groups_copy['unmatched']==False
    return_groups_copy.loc[index,matched_rows_first.columns]=return_groups.loc[index,matched_rows_first.columns]
    return_groups_copy.drop(columns=['b_i','unmatched'],inplace=True)
    return matched_rows,return_groups_copy,all_units_in_g
