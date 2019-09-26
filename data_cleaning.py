# -*- coding: utf-8 -*-
"""

@author: Neha
"""
import pandas as pd
import sys

def process_command_line(args):
    
    try:
        f = open(args.file_name[0], 'r')
    except TypeError:
        print('Invalid input error. See help for required inputs')
        sys.exit(1)
    df = pd.read_csv(args.file_name[0])
    treatment_column_name =  args.treatment_column_name[0]
    outcome_column_name = args.outcome_column_name[0]
    weight_array = [float(item) for item in args.weight_array[0].split(',')]
    adaptive_weights = args.adaptive_weights[0]

    return process_input_file(df, treatment_column_name, weight_array, \
                              outcome_column_name, adaptive_weights)

def process_input_file(df, treatment_column_name, weight_array,
                       outcome_column_name, adaptive_weights):
    
    
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
            
    
    return df, treatment_column_name, weight_array, outcome_column_name, adaptive_weights