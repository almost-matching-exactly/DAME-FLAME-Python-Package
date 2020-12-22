# -*- coding: utf-8 -*-
"""
Cleans data prior to doing matching. Called by the matching.py file.
"""
# author: Neha Gupta, Duke University
# Copyright Duke University 2020
# License: MIT

import pandas as pd
import numpy as np
import math

from . import early_stops

def read_files(input_data, holdout_data):
    """Both options can be either df or csv files and are parsed here.

    Input:
        input_data: The matching data as string filename or df
        holdout_data: The holdout data as string filename, df, fraction, bool

    Return:
        input_data: dataframe
        holdout_data: dataframe
    """

    # Read the input data
    if type(input_data) == pd.core.frame.DataFrame:
        df = input_data

    elif input_data == False:
        raise Exception("Need to specify either csv file name or pandas data "\
                        "frame in parameter 'input_data'")
    else:
        df = pd.read_csv(input_data)

    # Now read the holdout data
    if (type(holdout_data) == pd.core.frame.DataFrame):
        df_holdout = holdout_data
    elif (type(holdout_data) == float and holdout_data <= 1.0
          and holdout_data > 0.0):
            df_holdout = df.sample(frac=holdout_data)

    elif (holdout_data == False):
        df_holdout = df.sample(frac=0.1) # default if it's not provided is df.

    else:
        df_holdout = pd.read_csv(holdout_data)

    df.columns=map(str,df.columns)
    df_holdout.columns = map(str, df_holdout.columns)

    return df, df_holdout

def check_stops(stop_unmatched_c, early_stop_un_c_frac, stop_unmatched_t,
                early_stop_un_t_frac, early_stop_pe, early_stop_pe_frac,
                early_stop_iterations):
    """Check the parameters passed to DAME/FLAME relating to early stopping"""

    # todo: add check for epsilon on FLAME

    early_stops_obj = early_stops.EarlyStops()

    if (early_stop_un_t_frac > 1.0 or early_stop_un_t_frac < 0.0):
        raise Exception('The value provided for the early stopping critera '\
                        'of proportion of unmatched treatment units needs to '\
                        'be between 0.0 and 1.0')

    if (early_stop_un_c_frac > 1.0 or early_stop_un_c_frac < 0.0):
        raise Exception('The value provided for the early stopping critera '\
                        'of proportion of unmatched control units needs to '\
                        'be between 0.0 and 1.0')

    if (early_stop_pe == True):
        early_stop_pe = early_stop_pe_frac
    if (early_stop_pe_frac > 1.0 or early_stop_pe_frac < 0.0):
        raise Exception('The value provided for the early stopping critera of'\
                        ' PE needs to be between 0.0 and 1.0')

    if (type(early_stop_iterations) != int and early_stop_iterations != False):
        raise Exception('The value provided for early_stop_iteration needs '\
                        'to be an integer number of iterations, or False if '\
                        'not stopping early based on the number of iterations')

    # Put all of those parameters into the object to return
    early_stops_obj.unmatched_c = stop_unmatched_c
    early_stops_obj.unmatched_t = stop_unmatched_t
    early_stops_obj.un_c_frac = early_stop_un_c_frac
    early_stops_obj.un_t_frac = early_stop_un_t_frac
    early_stops_obj.pe = early_stop_pe
    early_stops_obj.iterations = early_stop_iterations

    return early_stops_obj

def check_parameters(adaptive_weights, df_holdout, df, alpha, FLAME,
                     weight_array=[], C=0.0):
    '''
    This function processes the parameters that were passed to DAME/FLAME
    that aren't directly the input file or related to stop_criteria.
    '''

    # Checks on the weight array...if the weight array needs to exist
    if (adaptive_weights == False):

        if (type(weight_array) != list):
            raise Exception('Invalid input error. A weight array of type'\
                            'array needs to be provided when the'\
                            'parameter adaptive_weights == True')

        # Confirm that weight array has the right number of values in it
        # Subtracting 2 because one col is the treatment and one is outcome.
        if (len(weight_array) != (len(df.columns)-2)):
            raise Exception('Invalid input error. Weight array size not equal'\
                            ' to number of columns in dataframe')

        # Confirm that weights in weight vector add to 1.
        if (abs(sum(weight_array) - 1.0) >= 0.001):
            # I do this weird operation instead of seeing if it equals one
            # to avoid floatig point addition errors that can occur.
            raise Exception('Invalid input error. Weight array values must '\
                            'sum to 1.0')

    else:
        # make sure that the alpha is valid if it's a ridge regression.
        if ((adaptive_weights == 'ridge' or adaptive_weights == "ridgeCV") and (alpha < 0.0)):
            raise Exception('Invalid input error. The alpha needs to be '\
                            'positive for ridge regressions.')

        # make sure that adaptive_weights is a valid value.
        if (adaptive_weights != "ridge" and
            adaptive_weights != "decisiontree" and
            adaptive_weights != "ridgeCV" and
            adaptive_weights != "decisiontreeCV"):
            raise Exception("Invalid input error. The acceptable values for "\
                            "the adaptive_weights parameter are 'ridge', "\
                            "'decisiontree', 'decisiontreeCV', or 'ridgeCV'. Additionally, "\
                            "adaptive-weights may be 'False' along "\
                            "with a weight array")


        # make sure the two dfs have the same number of columns first:
        if (len(df.columns) != len(df_holdout.columns)):
            raise Exception('Invalid input error. The holdout and main '\
                            'dataset must have the same number of columns')

        # make sure that the holdout columns match the df columns.
        if (set(df_holdout.columns) != set(df.columns)):
            # they don't match
            raise Exception('Invalid input error. The holdout and main '\
                            'dataset must have the same columns')

    if (FLAME == True):
        if (C < 0.0):
           raise Exception('The C, or the hyperparameter to trade-off between'\
                           ' balancing factor and predictive error must be '\
                           ' nonnegative. ')

    return

def replace_unique_large(df, treatment_column_name, outcome_column_name,
                         missing_indicator):
    ''' (helper)
    This function replaces missing values from the df with unique large values
    could possibly clean this up later
    '''
    # now we replace all of the missing_indicators with unique large vals
    # that are larger than max_val.

    df = df.replace(missing_indicator, np.nan)

    for col in df.columns:
        if (col != treatment_column_name and col != outcome_column_name):
            max_val = df[col].max()
            for item_num in df.index.values:
                if (math.isnan(df[col][item_num]) == True):
                    df.loc[item_num, col] = max_val + 1
                    max_val += 1

    cols = list(df.columns)
    cols.remove(outcome_column_name)
    df.loc[:,cols] = df.loc[:, cols].astype('int64')

    return df

def drop_missing(df, treatment_column_name, outcome_column_name,
                 missing_indicator):
    '''
    helper, this function drops rows that have missing_indicator in any of the cols
    '''

    if type(missing_indicator) != str and math.isnan(missing_indicator) == True:
        # either the missing indicator is already NaN and we just drop those rows
        df = df.dropna().copy()
    else:
        # but if its not NaN, switch missing_indicator with nan and then drop
        df = df.replace(missing_indicator, np.nan)
        df = df.dropna().copy()


    return df

def check_missings(df, df_holdout,  missing_indicator, missing_data_replace,
                   missing_holdout_replace, missing_holdout_imputations,
                   missing_data_imputations, treatment_column_name,
                   outcome_column_name, adaptive_weights):
    '''
    This function deals with all the missing data related stuff
    '''
    # No missing data allowed in the fixed weights version.
    # This is because having a weight array for pre-determined weights wouldn't
    # make sense...how would a user have even predetermined the weights?
    # If this is changed later, pay attention to MICE case (multiple weight
    # arrays needed?) and also sorting columns in replace unique large.
    if (missing_data_replace != 0 and adaptive_weights == False):
        raise Exception('Invalid input error. We do not support missing data '\
                        'handing in the fixed weights version of algorithms')

    mice_on_matching = False
    mice_on_holdout = False
    if (missing_data_replace == 0 and df.isnull().values.any() == True):
        print('There is missing data in this dataset. The default missing '\
              'data handling is being done, so we are not matching on '\
              'any missing values in the matching set')
        missing_data_replace = 2

        # TODO: iterate through all the columns and check for non-integer values
        # and then replace them with nan if needed.
        # df['hi'] = pd.to_numeric(df['hi'], errors='coerce')


    if (missing_data_replace == 1):
        df = drop_missing(df, treatment_column_name, outcome_column_name,
                          missing_indicator)

    if (missing_data_replace == 2):
        # so replacing with large unique values will only work if columns
        # are in order!!

        df = replace_unique_large(df, treatment_column_name,
                                  outcome_column_name, missing_indicator)

        # Reorder if they're not in order:
        df = df.loc[:, df.max().sort_values(ascending=True).index]

    if (missing_data_replace == 3):
        # this means do mice but only if theres something actually missing.
        df = df.replace(missing_indicator, np.nan)
        if df.isnull().values.any() == True:
            mice_on_matching = missing_data_imputations

    if (missing_holdout_replace == 0 and
        df_holdout.isnull().values.any() == True):
        print('There is missing data in this dataset. The default missing '\
              'data handling is being done, so we are running MICE on 10 '\
              'imputed holdout datasets')
        missing_holdout_replace = 2

    if (missing_holdout_replace == 1):
        df_holdout = drop_missing(df_holdout, treatment_column_name,
                                  outcome_column_name, missing_indicator)

    if (missing_holdout_replace == 2):
        # this means do mice.
        df_holdout = df_holdout.replace(missing_indicator, np.nan)
        # but if there is actually nothing missing in the dataset, then dont
        # need to do this.
        if (df_holdout.isnull().values.any() == True):
            mice_on_holdout = missing_holdout_imputations

    # converts float inputs to ints
    if mice_on_matching == False:
        try:
            cols = list(df.columns)
            cols.remove(outcome_column_name)
            df.loc[:, cols] = df.loc[:,cols].astype('int64')
        except:
            raise Exception('Invalid input error on matching dataset. Ensure all inputs asides from '\
                            'the outcome column are integers, and if missing' \
                            ' values exist, ensure they are handled.')
    if mice_on_holdout == False:
        try:
            cols = list(df_holdout.columns)
            cols.remove(outcome_column_name)
            df_holdout.loc[:, cols] = df_holdout[cols].astype('int64')
        except:
            raise Exception('Invalid input error on holdout dataset. Ensure all inputs asides from '\
                            'the outcome column are integers, and if missing' \
                            ' values exist, ensure they are handled.')

    return df, df_holdout, mice_on_matching, mice_on_holdout

def process_input_file(df, treatment_column_name, outcome_column_name,
                       adaptive_weights):
    '''
    This function processes the parameters passed to DAME/FLAME that are
    directly the input file.

    '''

    # Confirm that the treatment column name exists.
    if (treatment_column_name not in df.columns):
        raise Exception('Invalid input error. Treatment column name does not'\
                        ' exist')

    # Confirm that the outcome column name exists.
    if (outcome_column_name not in df.columns):
        raise Exception('Invalid input error. Outcome column name does not'\
                        ' exist')

    # column only has 0s and 1s.
    if (set(df[treatment_column_name].unique()) != {0,1}):
        raise Exception('Invalid input error. All rows in the treatment '\
                        'column must have either a 0 or a 1 value.')

    return df
