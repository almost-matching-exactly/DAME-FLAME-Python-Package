# -*- coding: utf-8 -*-
"""
@author: Neha, Tianyu
"""
import pandas as pd
import numpy as np


''' 
Group by match of FLAME algorithm.
'''

# This one is my edit of Tianyu's code...Nearly copied verbatim from Tianyu,
# Except I made changes, to lidx_wo_t and lidx_w_t
def match_ng(df, covs, covs_max_list, treatment_indicator_col = 'treated'):
    
    # this function takes a dataframe, a set of covariates to match on, 
    # the treatment indicator column and the matched indicator column.
    # it returns the array indicating whether each unit is matched (the first return value), 
    # and a list of indices for the matched units (the second return value)

    arr_slice_wo_t = df[covs].values # the covariates values as a matrix
    arr_slice_w_t = df[ covs + [treatment_indicator_col] ].values # the covariate values together with the treatment indicator as a matrix
    lidx_wo_t = np.dot( arr_slice_wo_t, np.array([ covs_max_list[i]**(i) for i in range(len(covs_max_list))]) ) # matrix multiplication, get a unique number for each unit
    lidx_w_t = np.dot( arr_slice_w_t, np.array([ covs_max_list[i]**(i+1) for i in range(len(covs_max_list))] + [1]) ) # matrix multiplication, get a unique number for each unit with treatment indicator
    _, unqtags_wo_t, counts_wo_t = np.unique(lidx_wo_t, return_inverse=True, return_counts=True) # count how many times each number appears
    _, unqtags_w_t, counts_w_t = np.unique(lidx_w_t, return_inverse=True, return_counts=True) # count how many times each number appears (with treatment indicator)
    
    match_indicator = ~(counts_w_t[unqtags_w_t] == counts_wo_t[unqtags_wo_t]) # a unit is matched if and only if the counts don't agree

    #print(match_indicator.shape)
    
    return match_indicator, lidx_wo_t[match_indicator]

'''
This function copied verbatim from 
https://github.com/ty-w/FLAME/blob/master/FLAMEbit.py#L177
 '''
def match(df, covs, covs_max_list, treatment_indicator_col = 'treated', match_indicator_col = 'matched'):
    
    # this function takes a dataframe, a set of covariates to match on, 
    # the treatment indicator column and the matched indicator column.
    # it returns the array indicating whether each unit is matched (the first return value), 
    # and a list of indices for the matched units (the second return value)
    
    arr_slice_wo_t = df[covs].values # the covariates values as a matrix
    arr_slice_w_t = df[ covs + [treatment_indicator_col] ].values # the covariate values together with the treatment indicator as a matrix
        
    lidx_wo_t = np.dot( arr_slice_wo_t, np.array([ covs_max_list[i]**(len(covs_max_list) - 1 - i) for i in range(len(covs_max_list))]) ) # matrix multiplication, get a unique number for each unit
    lidx_w_t = np.dot( arr_slice_w_t, np.array([ covs_max_list[i]**(len(covs_max_list) - i) for i in range(len(covs_max_list))] +                                               [1]
                                              ) ) # matrix multiplication, get a unique number for each unit with treatment indicator
        
    _, unqtags_wo_t, counts_wo_t = np.unique(lidx_wo_t, return_inverse=True, return_counts=True) # count how many times each number appears
    _, unqtags_w_t, counts_w_t = np.unique(lidx_w_t, return_inverse=True, return_counts=True) # count how many times each number appears (with treatment indicator)
    
    match_indicator = ~(counts_w_t[unqtags_w_t] == counts_wo_t[unqtags_wo_t]) # a unit is matched if and only if the counts don't agree
        
    return match_indicator, lidx_wo_t[match_indicator]