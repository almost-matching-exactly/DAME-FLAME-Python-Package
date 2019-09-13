# -*- coding: utf-8 -*-
"""
DAME Code

This package implements the code in the paper "Interpretable Almost-Exact 
Matching For Causual Inference" (Liu, Dieng, Roy, Rudin, Volfovsky) 
TODO: Insert Arxiv Link Here

This file in particular though, is just a wrapper that accepts user input and 
kicks off the input parsing, algo, etc. 

Example:
    TODO: Insert example here
    
    $ python main.py TODO: commandlines....
        

@author: Neha
"""

import argparse
import data_cleaning
import dame_algorithm
import match_quality
import pandas as pd


def main():
    
    # parse commandline arguments.
    print("here")
    
    parser = argparse.ArgumentParser(description="Implement the matching \
                                     method from the paper, Interpretable \
                                     Almost-Exact Matching for Causal \
                                     Inference")

    parser.add_argument('--valid_group_by', nargs='?', type=str, 
                        const='bit-vector', 
                        help='enter bit-vector or sql (default: bit-vector)')
    
    
    parser.add_argument('--file_name', nargs=1, type=str,
                        help='enter name of input file')
    
    parser.add_argument('--treatment_column_name', nargs=1, type=str,
                        help='enter the name of the column that has the \
                              boolean value for treatment or control group')
    
    parser.add_argument('--weight_array', nargs=1, type=str,
                        help='enter a comma separated string indicating the \
                        weights of \
                        the coefficients, predetermined from a ML algorithm. \
                        Must be the length of the number of coefficients.')
    
    parser.add_argument('--outcome_column_name', nargs=1, type=str,
                        help='enter the name of the column that has the \
                              value for outcome value')

    parser.add_argument('--adaptive_weights', nargs=1, type=str,
                        help='Enter True if want to decide to drop weights\
                        based on a ridge regression on hold-out training set\
                        or false (default) if want to decide to drop weights\
                        based on the weights given in the weight_array')
    
    parser.add_argument('--holdout_file_name', nargs=1, type=str,
                        help='Enter True if want to decide to drop weights\
                        based on a ridge regression on hold-out training set\
                        or false (default) if want to decide to drop weights\
                        based on the weights given in the weight_array')
    
    # TODO: add option for accepting a dataframe
    # TODO: output options. 
    
    args = parser.parse_args()

    # Process input command line options and for valid inputs
    df, treatment_column_name, \
        weight_array, outcome_column_name, \
        adaptive_weights = data_cleaning.process_command_line(args)
    
    
    return_covs_list, return_matched_group, \
        return_matched_data, return_pe = dame_algorithm.algo1(df,
                                                    treatment_column_name,
                                                    weight_array,
                                                    outcome_column_name,
                                                    adaptive_weights)
    
def DAME(valid_group_by='bit-vector', file_name = 'sample4.csv', 
         treatment_column_name = 'treated', weight_array = [0.25, 0.05, 0.7],
         outcome_column_name='outcome',
         adaptive_weights=False, holdout_file_name='sample4.csv'):
    
    # TODO: another input check, if adaptive_weight=True, then need holdout
        
    df = pd.read_csv(file_name)
    df_holdout = pd.read_csv(holdout_file_name)
    
    df, treatment_column_name, \
        weight_array, outcome_column_name = data_cleaning.process_input_file(df, \
                                                        treatment_column_name,\
                                                        weight_array, \
                                                        outcome_column_name)
        
    df_holdout, _, _, _ = data_cleaning.process_input_file(df, \
                                                        treatment_column_name,\
                                                        weight_array, \
                                                        outcome_column_name)
        
    return_covs_list, return_matched_group, \
        return_matched_data, return_pe = dame_algorithm.algo1(df,
                                                    treatment_column_name,
                                                    weight_array,
                                                    outcome_column_name,
                                                    adaptive_weights,
                                                    df_holdout)
    
    return return_covs_list, return_matched_group, return_matched_data, return_pe
    
if __name__ == "__main__":
    main()