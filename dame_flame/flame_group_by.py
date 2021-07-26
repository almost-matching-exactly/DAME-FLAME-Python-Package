# -*- coding: utf-8 -*-
""" Group-by bit match for FLAME algorithm, from "Fast Large..."(Wang etal)"""

# author: Neha Gupta, Tianyu Wang, Duke University
# Copyright Duke University 2020
# License: MIT

import numpy as np

def match_ng(df, covs, covs_max_list, treatment_indicator_col='treated'):
    '''
    This is the match_ng function
    '''
    # this function takes a dataframe, a set of covariates to match on,
    # the treatment indicator column and the matched indicator column.
    # it returns the array indicating whether each unit is matched (the first return value),
    # and a list of indices for the matched units (the second return value)

    np.seterr(all='raise')
    arr_slice_wo_t = df[covs].values # the covariates values as a matrix

    # the covariate values together with the treatment indicator as a matrix
    arr_slice_w_t = df[covs + [treatment_indicator_col]].values

    # matrix multiplication, get a unique number for each unit
    b_i = np.dot(arr_slice_wo_t, np.power(covs_max_list, [i for i in range(len(covs_max_list))]))

    # matrix multiplication, get a unique number for each unit with treatment indicator
    b_i_plus = np.dot(arr_slice_w_t, np.append(np.power(covs_max_list, [i+1 for i in range(len(covs_max_list))]), [1]))
    # b_i_plus = np.dot(arr_slice_w_t, np.array([covs_max_list[i]**(i+1) for i in range(len(covs_max_list))] + [1]))

    # count how many times each number appears
    # unqtags_wo_t is index of the first occurrence of each unique val in b_i
    # c_i is the index to reconstruct the original array from the unique array
    _, unqtags_wo_t, c_i = np.unique(b_i, return_inverse=True,
                                     return_counts=True)

    # count how many times each number appears (with treatment indicator)
    _, unqtags_w_t, c_i_plus = np.unique(b_i_plus, return_inverse=True,
                                         return_counts=True)

    # a unit is matched if and only if the counts don't agree
    match_indicator = ~(c_i_plus[unqtags_w_t] == c_i[unqtags_wo_t])
    return match_indicator, b_i[match_indicator]
