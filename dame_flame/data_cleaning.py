# -*- coding: utf-8 -*-
"""

@author: Neha
"""

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
                early_stop_bf, early_stop_bf_frac, early_stop_iterations):
    """Check the parameters passed to DAME/FLAME relating to early stopping"""
    
    early_stops_obj = early_stops.EarlyStops()
    
    # todo: pretty sure we don't need this one after thinking about it a bit
    # but check with team. Because maybe you want to match as many as possible
    # of both, and just stop when there's no more covar sets to check? 
    
    # Validate
    #if (stop_unmatched_c == False and stop_unmatched_t == False):
    #   raise Exception('Either stop_unmatched_c or stop_unmatched_t, or both'\
    #         ' must be true, so the algorithm terminates if there are no '\
    #         'units left to match')
    
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
    if (early_stop_bf == True):
        early_stop_bf = early_stop_bf_frac
    if (early_stop_bf_frac > 1.0 or early_stop_bf_frac < 0.0):
        raise Exception('The value provided for the early stopping critera of'\
                        'BF needs to be between 0.0 and 1.0')
        
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
    early_stops_obj.bf = early_stop_bf
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
        
        if (FLAME == True):
            raise Exception('adaptive-weights must be either ridge, ridgeCV,'\
                            ' or decision-tree for FLAME algorithm')
            
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
        if (adaptive_weights == 'ridge' and (alpha < 0.0)):
            raise Exception('Invalid input error. The alpha needs to be '\
                            'positive for ridge regressions.')    
            
        if (adaptive_weights == 'ridgeCV' and (alpha == 0.1)):
            print('You did not provide a list of alphas for ridgeCV. The '\
                  'default of [0.001, 0.01, 0.1, 1, 2, 5, 10] will be used')
            alpha = [0.001, 0.01, 0.1, 1, 2, 5, 10]
        
        # make sure that adaptive_weights is a valid value.
        if (adaptive_weights != "ridge" and 
            adaptive_weights != "decision tree" and
            adaptive_weights != "ridgeCV"):
            raise Exception("Invalid input error. The acceptable values for "\
                            "the adaptive_weights parameter are 'ridge', "\
                            "'decision tree', or 'ridgeCV'. Additionally, "\
                            "for DAME, adaptive-weights may be 'False' along "\
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
            
    return alpha

def replace_unique_large(df, treatment_column_name, outcome_column_name,
                         missing_indicator):
    ''' (helper)
    This function replaces missing values from the df with unique large values
    could possibly clean this up later
    '''
    max_val = df.max().max()
    # now we replace all of the missing_indicators with unique large vals
    # that are larger than max_val. 

    df = df.replace(missing_indicator, np.nan)
    
    for col in df.columns:
        if (col != treatment_column_name and col != outcome_column_name):
            for item_num in df.index.values:
                if (math.isnan(df[col][item_num]) == True):
                    df.loc[item_num, col] = max_val + 1
                    max_val += 1
                    
    return df

def drop_missing(df, treatment_column_name, outcome_column_name, 
                 missing_indicator):
    ''' 
    helper, this function drops rows that have missing_indicator in any of the cols
    '''
    
    if math.isnan(missing_indicator) == True:
        # either the missing indicator is already NaN and we just drop those rows
        df = df.dropna()
    else:
        # but if its not NaN, switch missing_indicator with nan and then drop
        df = df.replace(missing_indicator, np.nan)
        df = df.dropna()
    
    return df
    
def check_missings(df, df_holdout,  missing_indicator, missing_data_replace,
                   missing_holdout_replace, missing_holdout_imputations,
                   missing_data_imputations, treatment_column_name, 
                   outcome_column_name):
    '''
    This function deals with all the missing data related stuff
    '''
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
        # this means do mice ugh lol. 
        df_holdout = df_holdout.replace(missing_indicator, np.nan)
        # but if there is actually nothing missing in the dataset, then dont
        # need to do this. 
        if (df_holdout.isnull().values.any() == True):
            mice_on_holdout = missing_holdout_imputations
    
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
        
    if (adaptive_weights == False):
        # Ensure that the columns are sorted in order: binary, tertary, etc
        max_column_size = 1
        for col_name in df.columns:
            if ((col_name != treatment_column_name) and 
                (col_name != outcome_column_name)):
                # Todo: before, this was df[col_name].unique().max(), which I removed when it didnt work
                # this seems to work, but I wonder if it's a happy accident
                # because, https://stackoverflow.com/questions/21319929/how-to-determine-whether-a-pandas-column-contains-a-particular-value
                if (df[col_name].max() >= max_column_size):
                    max_column_size = df[col_name].max()
                else:
                    raise Exception('Invalid input error. Dataframe column '\
                                    'size must be in increasing order from '\
                                    'left to right.')
    
    else:
        # Reorder if they're not in order:
        df = df.loc[:, df.max().sort_values(ascending=True).index]
                
        
        

    return df