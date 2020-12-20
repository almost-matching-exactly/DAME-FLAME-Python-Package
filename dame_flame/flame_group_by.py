# -*- coding: utf-8 -*-
""" Group-by bit match for FLAME algorithm, from "Fast Large..."(Wang etal)"""

# author: Neha Gupta, Tianyu Wang, Duke University
# Copyright Duke University 2020
# License: MIT

import pandas as pd
import numpy as np

def match_ng(df, covs, covs_max_list, treatment_indicator_col = 'treated'):

    # this function takes a dataframe, a set of covariates to match on,
    # the treatment indicator column and the matched indicator column.
    # it returns the array indicating whether each unit is matched (the first return value),
    # and a list of indices for the matched units (the second return value)

    arr_slice_wo_t = df[covs].values # the covariates values as a matrix
    arr_slice_w_t = df[ covs + [treatment_indicator_col] ].values # the covariate values together with the treatment indicator as a matrix
    b_i = np.dot( arr_slice_wo_t, np.array([ covs_max_list[i]**(i) for i in range(len(covs_max_list))]) ) # matrix multiplication, get a unique number for each unit
    b_i_plus = np.dot( arr_slice_w_t, np.array([ covs_max_list[i]**(i+1) for i in range(len(covs_max_list))] + [1]) ) # matrix multiplication, get a unique number for each unit with treatment indicator
    _, unqtags_wo_t, c_i = np.unique(b_i, return_inverse=True, return_counts=True) # count how many times each number appears
    _, unqtags_w_t, c_i_plus = np.unique(b_i_plus, return_inverse=True, return_counts=True) # count how many times each number appears (with treatment indicator)

    match_indicator = ~(c_i_plus[unqtags_w_t] == c_i[unqtags_wo_t]) # a unit is matched if and only if the counts don't agree

    return match_indicator, b_i[match_indicator]
