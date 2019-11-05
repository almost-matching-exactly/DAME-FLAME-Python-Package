# -*- coding: utf-8 -*-
"""
DAME Python Package

This package implements the code in the paper:
    "Interpretable Almost-Exact 
Matching For Causual Inference" (Liu, Dieng, Roy, Rudin, Volfovsky) 
https://arxiv.org/abs/1806.06802

This file in particular is just a wrapper that accepts user input and 
kicks off the input parsing, algo, etc. 

Example:
    DAME(file_name='sample2.csv', treatment_column_name='treated', 
    outcome_column_name='outcome', adaptive_weights=True, 
    holdout_file_name='sample2.csv', ate=False, repeats=False)

@author: Neha
"""
import pandas as pd
import argparse
import data_cleaning
import dame_algorithm
import query_mmg
import query_ate
import flame_algorithm

def DAME(file_name = 'sample4.csv', 
         treatment_column_name = 'treated', weight_array = [0.25, 0.05, 0.7],
         outcome_column_name='outcome',
         adaptive_weights=False, holdout_file_name=False,
         repeats=True, want_pe=False):
    """
    This function kicks off the DAME algorithm

    Args:
        file_name: The csv file with the data being matched
        treatment_column_name: Indicates the name
            of the column that contains the binary indicator for whether each
            row is a treatment group or not.
        weights: As provided by the user, array of weights of all covariates 
            that are in df_all. Only needed if adaptive_weights = True.
        outcome_column_name: Indicates the name
            of the column that contains the outcome values. 
        adaptive_weights: This is true if decide to drop 
            weights based on a ridge regression on hold-out training set
            or false (default) if decide to drop weights
            based on the weights given in the weight_array
        holdout_file_name: If doing an adaptive_weights version, for training
        ate: Bool, whether to output the ATE value for the matches.
        repeats: Bool, whether or not values for whom a MMG has been found can
            be used again and placed in an auxiliary matched group.

    Returns:
        return_df: df of units with the column values of their main matched
            group, with "*"s in place for the columns not in their MMG
    """
    
    df, df_holdout = data_cleaning.read_files(file_name, holdout_file_name)
        
    data_cleaning.process_input_file(df, treatment_column_name,
                                     outcome_column_name)

    data_cleaning.check_parameters(adaptive_weights, weight_array, 
                                                df_holdout, df)
   
    return_df =  dame_algorithm.algo1(df, treatment_column_name, weight_array,
                                outcome_column_name, adaptive_weights,
                                df_holdout, repeats, want_pe)

    return return_df

def FLAME(file_name = 'sample4.csv', 
         treatment_column_name = 'treated', weight_array = [0],
         outcome_column_name='outcome',
         adaptive_weights=False, holdout_file_name='sample4.csv',
         repeats=True, pre_dame=False):
    """
    This function kicks off the FLAME algorithm.
    
    Args:
        See DAME above.
        pre_dame (int, False): Indicates whether to switch to dame and after
            int number of iterations. 
    Returns:
        See DAME above.
    """
    
    df, df_holdout = data_cleaning.read_files(file_name, holdout_file_name)
        
    data_cleaning.process_input_file(df, treatment_column_name,
                                     outcome_column_name)

    data_cleaning.check_parameters(adaptive_weights, weight_array, 
                                                df_holdout, df)
    
    return_df =  flame_algorithm.flame_generic(df, treatment_column_name, weight_array,
                                               outcome_column_name, adaptive_weights,
                                               df_holdout, repeats, pre_dame)
    return return_df

def mmg_of_unit(return_df, unit_id, file_name):
    """
    This function allows a user to find the main matched group of a particular
    unit, after the main DAME algorithm has already been run and all matches
    have been found. 
    
    Args:
        return_df: The return value from DAME above
        unit_id(int): the unit aiming to find the mmg of
        file_name: The csv file containing all of the original data.
    """
    df = pd.read_csv(file_name)
    return query_mmg.find(return_df, unit_id, df)

def ate_of_unit(return_df, unit_id, file_name, treatment_column_name, outcome_column_name):
    """
    This function allows a user to find the main matched group of a particular
    unit, after the main DAME algorithm has already been run and all matches
    have been found. 
    
    Args:
        return_df: The return value from DAME above
        unit_id: the unit aiming to find the mmg of
        file_name: The csv file containing all of the original data.
    """
    df_mmg = mmg_of_unit(return_df, unit_id, file_name)
    
    df_all = pd.read_csv(file_name)
    return query_ate.find(df_mmg, unit_id, df_all, treatment_column_name, outcome_column_name)
