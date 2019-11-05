# -*- coding: utf-8 -*-
"""

@author: Neha
"""
import pandas as pd
import sys

def read_files(file_name, holdout_file_name):
    try:
        df = pd.read_csv(file_name)
        if holdout_file_name != False:
            df_holdout = pd.read_csv(holdout_file_name)
        else:
            # the default df_holdout if it's not provided is the df
            df_holdout = df
    except ValueError:
        print('Files could not be found')
        sys.exit(1)
    
    return df, df_holdout

def check_parameters(adaptive_weights, weight_array, df_holdout, df):
    '''
    This function processes the parameters that were passed to DAME/FLAME
    that aren't directly the input file.
    '''
            
    # Checks on the weight array...if the weight array needs to exist
    if adaptive_weights == False:
        
        # Confirm that weight array has the right number of values in it
        # Subtracting 2 because one col is the treatment and one is outcome. 
        if len(weight_array) != (len(df.columns)-2):
            print('Invalid input error. Weight array size not equal to number \
                  of columns in dataframe')
            sys.exit(1)
        
        # Confirm that weights in weight vector add to 1.
        if sum(weight_array) != 1.0:
            print('Invalid input error. Weight array values must sum to 1.0')
            sys.exit(1)
            
    else:
        
        # make sure the two dfs have the same number of columns first:
        if (len(df.columns) != len(df_holdout.columns)):
            print('Invalid input error. The holdout and main dataset \
                  must have the same number of columns')
            sys.exit(1)
        # make sure that the holdout columns match the df columns.
        if (False in (df_holdout.columns == df.columns)):
            # they don't match
            print('Invalid input error. The holdout and main dataset \
                  must have the same columns')
            sys.exit(1)
                
            
    return

def process_input_file(df, treatment_column_name, outcome_column_name):
    '''
    This function processes the parameters passed to DAME/FLAME that are 
    directly the input file.
    
    '''
    
    # Confirm that the treatment column name exists. 
    if treatment_column_name not in df.columns:
        print('Invalid input error. Treatment column name does not exist')
        sys.exit(1)
        
    # Confirm that the outcome column name exists. 
    if outcome_column_name not in df.columns:
        print('Invalid input error. Outcome column name does not exist')
        sys.exit(1)
        
    # column only has 0s and 1s. 
    if set(df[treatment_column_name].unique()) != {0,1}:
        print('Invalid input error. Treatment column must have 0 and 1 values')
        sys.exit(1)
        
    # Ensure that the columns are sorted in order: binary, tertary, etc
    max_column_size = 1
    for col_name in df.columns:
        if (col_name != treatment_column_name) and (col_name != outcome_column_name):
            if df[col_name].unique().max() >= max_column_size:
                max_column_size = df[col_name].unique().max()
            else:
                print('Invalid input error. Dataframe column size must be in \
                      increasing order from left to right.')
                sys.exit(1)
            
    
    return