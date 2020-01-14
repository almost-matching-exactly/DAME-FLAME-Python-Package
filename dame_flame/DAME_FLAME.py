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

x = DAME(input_data='sample5.csv', treatment_column_name='treated', 
outcome_column_name='outcome', adaptive_weights='ridge', 
holdout_data='sample5.csv', repeats=True, want_pe=False)

"""
import pandas as pd
import numpy as np

import data_cleaning
import dame_algorithm
import query_mmg
import query_ate
import flame_algorithm
import flame_dame_helpers
from early_stops import EarlyStops

def DAME(input_data = False,
         treatment_column_name = 'treated', weight_array = False,
         outcome_column_name='outcome',
         adaptive_weights='ridge', alpha = 0.1, holdout_data=False,
         repeats=True, verbose=0, want_pe=False, early_stop_iterations=False, 
         stop_unmatched_c=False, early_stop_un_c_frac = 0.1, 
         stop_unmatched_t=True, early_stop_un_t_frac = 0.1,
         early_stop_pe = False, early_stop_pe_frac = 0.01,
         want_bf=False, early_stop_bf=False, early_stop_bf_frac = 0.01,
         missing_indicator=np.nan, missing_data_replace=0,
         missing_holdout_replace=0, missing_holdout_imputations = 10,
         missing_data_imputations=0):
    """
    This function kicks off the DAME algorithm

    Args:
        input_data: The csv file with the data being matched or df. 
        treatment_column_name: Indicates the name
            of the column that contains the binary indicator for whether each
            row is a treatment group or not.
        weights: As provided by the user, array of weights of all covariates 
            that are in df_all. Only needed if adaptive_weights = True.
        outcome_column_name: Indicates the name
            of the column that contains the outcome values. 
        adaptive_weights: This is false (default) if decide to drop weights
            based on the weights given in the weight_array, or 'ridge', or 
            'decision tree'.
        alpha (float): This is the alpha for ridge regression. We use the scikit
            package for ridge regression, so it is "regularization strength"
            Larger values specify stronger regularization. 
            Must be positive float.
        holdout_data: If doing an adaptive_weights version, for training
        repeats: Bool, whether or not values for whom a MMG has been found can
            be used again and placed in an auxiliary matched group.
        early_stop_iterations (optional int): If provided, a number of iterations 
            to hard stop the algorithm after.
        stop_unmatched_c, stop_unmatched_t (bool, optional): specifies whether
            the algorithm stops when there are no units remaining to match
        early_stop_un_c_frac, early_stop_un_t_frac (optional float, 
            from 0.0 - 1.0): If provided, a fraction of unmatched control/
            treatment units. When threshold met, hard stop the algo.
        verbose (default: False, 0): If 1, provides iteration num, if 2 provides
            iteration number and number of units left to match on every 10th iter,
            if 3 does this print on every iteration. 
        missing_holdout_replace (0,1,2): default 0.
            if 0, assume no missing holdout data and proceed
            if 1, drop all missing_indicator values from holdout dataset
            if 2, do mice on holdout dataset for missing_holdout_imputatations
            number of imputations
        missing_data_replace (0,1,2,3): default 0.
            if 0, assume no missing data in matching data and proceed
            if 1, drop all missing_indicator values from matching data
            if 2, replace all missing_indicator values with unique large vals
            so they essentially get skipped in the matching
            if 3, do mice on matching dataset for missing_data_imputatations
            number of imputations.

    Returns:
        return_df: df of units with the column values of their main matched
            group, with "*"s in place for the columns not in their MMG
    """

    df, df_holdout = data_cleaning.read_files(input_data, holdout_data)
        
    df = data_cleaning.process_input_file(df, treatment_column_name,
                                     outcome_column_name, adaptive_weights)

    data_cleaning.check_parameters(adaptive_weights, weight_array, df_holdout, 
                                   df, alpha)
    df, df_holdout, mice_on_matching, mice_on_holdout = data_cleaning.check_missings(df, 
                                                   df_holdout, missing_indicator, 
                                                   missing_data_replace,
                                                   missing_holdout_replace, 
                                                   missing_holdout_imputations,
                                                   missing_data_imputations,
                                                   treatment_column_name,
                                                   outcome_column_name)
    
    early_stops = data_cleaning.check_stops(
            stop_unmatched_c, early_stop_un_c_frac, stop_unmatched_t,
            early_stop_un_t_frac, early_stop_pe, early_stop_pe_frac, 
            early_stop_bf, early_stop_bf_frac, early_stop_iterations)
        
    if (mice_on_matching == False):
        return dame_algorithm.algo1(df, treatment_column_name, weight_array,
                                    outcome_column_name, adaptive_weights, alpha,
                                    df_holdout, repeats, want_pe,
                                    verbose, want_bf,
                                    mice_on_holdout, early_stops)
    else:
        # this would mean we need to run mice on the matching data, which means
        # that we have to run algo1 multiple times
        print("Warning: You have opted to run MICE on the matching dataset. "\
              "This is slow, and not recommended. We recommend that instead, "\
              "you run the algorithm and skip matching on missing data points,"\
              "with the parameter missing_data_replace=2.")
        
        # first we get the imputed datasets
        df_array = flame_dame_helpers.create_mice_dfs(df, mice_on_matching)
        return_array = []
        for i in range(len(df_array)):
            return_array.append(dame_algorithm.algo1(df_array[i], treatment_column_name, weight_array,
                                    outcome_column_name, adaptive_weights, alpha,
                                    df_holdout, repeats, want_pe,
                                    verbose, want_bf,
                                    mice_on_holdout, early_stops))
        return return_array
    
    
def FLAME(input_data = False,
         treatment_column_name = 'treated', weight_array = False,
         outcome_column_name='outcome',
         adaptive_weights='ridge', alpha = 0.1, holdout_data=False,
         repeats=True, verbose=0, want_pe=False, early_stop_iterations=False, 
         stop_unmatched_c=False, early_stop_un_c_frac = 0.1, 
         stop_unmatched_t=True, early_stop_un_t_frac = 0.1,
         early_stop_pe = False, early_stop_pe_frac = 0.01,
         want_bf=False, early_stop_bf=False, early_stop_bf_frac = 0.01, 
         missing_indicator=np.nan, missing_data_replace=0,
         missing_holdout_replace=0, missing_holdout_imputations = 10,
         missing_data_imputations=0, pre_dame=False):
    """
    This function kicks off the FLAME algorithm.
    
    Args:
        See DAME above.
        pre_dame (int, False): Indicates whether to switch to dame and after
            int number of iterations. 
    Returns:
        See DAME above.
    """
    
    df, df_holdout = data_cleaning.read_files(input_data, holdout_data)
        
    df = data_cleaning.process_input_file(df, treatment_column_name,
                                     outcome_column_name, adaptive_weights)

    data_cleaning.check_parameters(adaptive_weights, weight_array, 
                                                df_holdout, df, alpha)
    
    df, df_holdout, mice_on_matching, mice_on_holdout = data_cleaning.check_missings(df, 
                                                   df_holdout, missing_indicator, 
                                                   missing_data_replace,
                                                   missing_holdout_replace, 
                                                   missing_holdout_imputations,
                                                   missing_data_imputations,
                                                   treatment_column_name,
                                                   outcome_column_name)

    early_stops = data_cleaning.check_stops(
            stop_unmatched_c, early_stop_un_c_frac, stop_unmatched_t,
            early_stop_un_t_frac, early_stop_pe, early_stop_pe_frac, 
            early_stop_bf, early_stop_bf_frac, early_stop_iterations)
    
    if (mice_on_matching == False):
        return flame_algorithm.flame_generic(df, treatment_column_name, weight_array,
                                outcome_column_name, adaptive_weights, alpha,
                                df_holdout, repeats, want_pe,
                                verbose, want_bf, mice_on_holdout, early_stops,
                                pre_dame)
    else:
        # this would mean we need to run mice on the matching data, which means
        # that we have to run algo1 multiple times
        print("Warning: You have opted to run MICE on the matching dataset. "\
              "This is slow, and not recommended. We recommend that instead, "\
              "you run the algorithm and skip matching on missing data points,"\
              "with the parameter missing_data_replace=2.")
        
        # first we get the imputed datasets
        df_array = flame_dame_helpers.create_mice_dfs(df, mice_on_matching)
        return_array = []
        for i in range(len(df_array)):
            return_array.append(flame_algorithm.flame_generic(df, treatment_column_name, weight_array,
                                outcome_column_name, adaptive_weights, alpha,
                                df_holdout, repeats, want_pe,
                                verbose, want_bf, mice_on_holdout, early_stops,
                                pre_dame))
            
        return return_array

def mmg_of_unit(return_df, unit_id, input_data, output_style=1):
    """
    This function allows a user to find the main matched group of a particular
    unit, after the main DAME algorithm has already been run and all matches
    have been found. 
    
    Args:
        return_df: The return value from DAME above
        unit_id(int): the unit aiming to find the mmg of
        file_name: The csv file containing all of the original data.
        output_style: 1 if you want just the covariates matched on, and 2 if
        you want all of the attributes listed. 
    """
    if type(input_data) == pd.core.frame.DataFrame:
        df = input_data
    else:
        df = pd.read_csv(return_df)
        
    mmg_df = query_mmg.find(return_df, unit_id, df)
    if mmg_df == False:
        print("This unit does not have any matches")
        return False
    
    if output_style == 2:
        return input_data.loc[mmg_df.index]
    else:
        # so now we need to filter on just the ones we want. 
        if ("*" in return_df.loc[unit_id].unique()):
            # this means there is a star and it needs to be filtered. 
            my_series = return_df.loc[unit_id]
            star_cols = my_series[my_series == "*"].index
            non_star_cols = input_data.columns.difference(star_cols)
            return input_data[non_star_cols].loc[mmg_df.index]
        else:
            # nothing to filter out, so same result as output_style=2
            return input_data.loc[mmg_df.index]
        

def te_of_unit(return_df, unit_id, input_data, treatment_column_name, outcome_column_name):
    """
    This function allows a user to find the treatment effect of a particular
    unit, after the main DAME algorithm has already been run and all matches
    have been found. 
    
    Args:
        return_df: The return value from DAME above
        unit_id: the unit aiming to find the mmg of. Type int.
        file_name: The csv file containing all of the original data.
    """
    df_mmg = mmg_of_unit(return_df, unit_id, input_data)
    if mmg_df == False:
        print("This unit does not have any matches, so can't find the "\
              "treatment effect")
        return False
    
    if type(input_data) == pd.core.frame.DataFrame:
        df = input_data
    else:
        df = pd.read_csv(return_df)
        
    return query_ate.find(df_mmg, unit_id, df, treatment_column_name, outcome_column_name)

##### These are fancy versions of the above functions for pretty prints, etc ######

def mmg_and_te_of_unit(return_df, unit_id, input_data, treatment_column_name, outcome_column_name, return_vals=1):
    """
    Fancy version of above function.
    """
    if return_vals == 0:
        return print_te_and_mmg(return_df, unit_id, input_data, treatment_column_name, outcome_column_name)
    
    df_mmg = mmg_of_unit(return_df, unit_id, input_data)
    if df_mmg == False:
        print("This unit does not have any matches")
        return False
    
    if type(input_data) == pd.core.frame.DataFrame:
        df = input_data
    else:
        df = pd.read_csv(return_df)
        
    return df_mmg, query_ate.find(df_mmg, unit_id, df, treatment_column_name, outcome_column_name)

def print_te_and_mmg(return_df, unit_id, input_data, treatment_column_name, outcome_column_name):
    """
    Fancy version of above function.
    """
    df_mmg = mmg_of_unit(return_df, unit_id, input_data)
    if df_mmg == False:
        print("This unit does not have any matches")
        return False
    
    te = te_of_unit(return_df, unit_id, input_data, treatment_column_name, outcome_column_name)
    
    print("This is the Main Matched Group of unit", unit_id, ":")
    print(df_mmg)
    print("This is the treatment effect of unit", unit_id, ":")
    print(te)