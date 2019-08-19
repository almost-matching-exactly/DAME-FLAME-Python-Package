# -*- coding: utf-8 -*-
"""
DAME Code

This package implements the code in the paper "Interpretable Almost-Exact 
Matching For Causual Inference" (Liu, Dieng, Roy, Rudin, Volfovsky) 
TODO: Insert Arxiv Link Here

Example:
    TODO: Insert example here
    
    $ python main.py TODO: commandlines....
        

@author: Neha
"""

import argparse
import data_cleaning
import dame_algorithms


def main():
    
    # parse commandline arguments.
    
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
    
    # TODO: add option for accepting a dataframe
    # TODO: output options. 
    
    args = parser.parse_args()

    # call functions to do things.
    df, treatment_column_name, weight_array = data_cleaning.process_input_file(args)
    
    
    return_covs_list, return_matched_group, return_matched_data = dame_algorithms.algo1(df, treatment_column_name, weight_array)
    
    
if __name__ == "__main__":
    main()