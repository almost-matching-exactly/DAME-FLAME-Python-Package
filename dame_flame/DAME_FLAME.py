# -*- coding: utf-8 -*-
""" Wrapper around user input, starting the input parsing and validation.
@author: Neha Gupta, Duke University

DAME-FLAME Python Package

This package provides a package for the DAME algorithm from the paper
"Interpretable Almost-Exact Matching For Causual Inference" 
(Liu, Dieng, Roy, Rudin, Volfovsky), https://arxiv.org/abs/1806.06802, as well 
as the FLAME algorithm from the paper "FLAME: A Fast Large-scale Almost
Matching Exactly Approach to Causal Inference" (Wang, Morucci, Awan, Liu, Roy,
Rudin, Volfovsky) https://arxiv.org/pdf/1707.06315.pdf

This file in particular is just a wrapper around the algorithms that accepts 
user input and kicks off the input parsing and validation prior to calling
the algorithms. 


For examples, see the main github page at:
https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/

"""
import pandas as pd
import numpy as np

from . import data_cleaning
from . import dame_algorithm
from . import query_mmg
from . import query_ate
from . import flame_algorithm
from . import flame_dame_helpers
from . import early_stops

def DAME(input_data=False, treatment_column_name='treated', weight_array=False,
         outcome_column_name='outcome', adaptive_weights='ridge', alpha=0.1, 
         holdout_data=False, repeats=True, verbose=2, want_pe=False, 
         early_stop_iterations=False, stop_unmatched_c=False, 
         early_stop_un_c_frac=False, stop_unmatched_t=False, 
         early_stop_un_t_frac=False, early_stop_pe=False, 
         early_stop_pe_frac=0.01, want_bf=False, early_stop_bf=False, 
         early_stop_bf_frac=0.01, missing_indicator=np.nan, 
         missing_data_replace=0, missing_holdout_replace=0, 
         missing_holdout_imputations=10, missing_data_imputations=0):
    """ Accepts user input, validates, error-checks, calls DAME algorithm.

    Args:
        input_data(str, df): The data being matched. 
        treatment_column_name (str): Indicates the name of the column that 
            contains the binary indicator for whether each row is a treatment 
            group or not.
        weight_array (array, bool): array of weights of all covariates that are
            in input_data. Only needed if adaptive_weights = False.
        outcome_column_name (str): Indicates the name of the column that 
            contains the outcome values. 
        adaptive_weights (bool, str): Weight dropping method. False, 'ridge', 
            'decision tree', or 'ridgeCV'.
        alpha (float): This is the alpha for ridge regression. We use the 
            scikit package for ridge regression, so it is "regularization 
            strength". Larger values specify stronger regularization. 
            Must be positive float.
        holdout_data (str, df): If doing an adaptive_weights version this is
            for the training step.
        repeats (bool): whether values for whom a MMG has been found can
            be used again and placed in an auxiliary matched group.
        early_stop_iterations (optional int): If provided, a number of iters 
            to hard stop the algorithm after.
        stop_unmatched_c, stop_unmatched_t (bools): specifies whether
            the algorithm stops when there are no units remaining to match
        early_stop_un_c_frac, early_stop_un_t_frac (optional float, 
            from 0.0 - 1.0): If provided, a fraction of unmatched control/
            treatment units. When threshold met, hard stop the algo.
        early_stop_pe, early_stop_bf: Whether the covariate set chosen to match
            on has a pe/bf lower than the parameter early_stop_pe_frac, at 
            which point the algorithm will stop.
        early_stop_pe_frac, early_stop_bf_frac: If early_stop_pe/bf is true, 
            then if the covariate set chosen to match on has a PE lower than 
            this value, the algorithm will stop
        verbose (default: 2): If 1, provides iteration num, if 2 provides
            iteration number and number of units left to match on every 10th 
            iter, if 3 does this print on every iteration. If 0, nothing. 
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
        missing_holdout_imputatations: If missing_holdout_replace=2, the number
            of imputations on the holdout set.
        missing_data_imputations: If missing_data_replace=3, the number of 
            imputations on the matching set. 
        missing_indicator: This is the character/number/np.nan that indicates 
            missing vals in the holdout/matching data. 
        want_pe: whether the output of the algorithm will include the 
            predictive error of the covariate sets matched on in each iteration
        want_bf: whether the output will include the balancing factor of each 
            iteration.

    Returns:
        return_df: df of units with the column values of their main matched
            group, with "*"s in place for the columns not in their 
        pe_array: If want_pe is true, then the PE values of each match
        bf_array: If want_bf is true, then the BF values of each match
            
    Raises:
        Exception: An error occurred in the data_cleaning.py file. 
    """

    df, df_holdout = data_cleaning.read_files(input_data, holdout_data)
        
    df = data_cleaning.process_input_file(
        df, treatment_column_name, outcome_column_name, adaptive_weights)

    alpha = data_cleaning.check_parameters(adaptive_weights, df_holdout, df, 
                                           alpha, False, weight_array)
    
    df, df_holdout, mice_on_match, mice_on_hold = data_cleaning.check_missings(
        df, df_holdout, missing_indicator, missing_data_replace,
        missing_holdout_replace, missing_holdout_imputations,
        missing_data_imputations, treatment_column_name, outcome_column_name)
    
    early_stops = data_cleaning.check_stops(
        stop_unmatched_c, early_stop_un_c_frac, stop_unmatched_t,
        early_stop_un_t_frac, early_stop_pe, early_stop_pe_frac, 
        early_stop_bf, early_stop_bf_frac, early_stop_iterations)
        
    if (mice_on_match == False):
        return dame_algorithm.algo1(
            df, treatment_column_name, weight_array, outcome_column_name, 
            adaptive_weights, alpha, df_holdout, repeats, want_pe, verbose, 
            want_bf, mice_on_hold, early_stops)
    else:
        # this would mean we need to run mice on the matching data, which means
        # that we have to run algo1 multiple times
        print("Warning: You have opted to run MICE on the matching dataset. "\
              "This is slow, and not recommended. We recommend that instead,"\
              " you run the algorithm and skip matching on missing data "\
              "points, with the parameter missing_data_replace=2.")
        
        # first we get the imputed datasets
        df_array = flame_dame_helpers.create_mice_dfs(df, mice_on_match)
        return_array = []
        for i in range(len(df_array)):
            return_array.append(dame_algorithm.algo1(
                df_array[i], treatment_column_name, weight_array,
                outcome_column_name, adaptive_weights, alpha, df_holdout, 
                repeats, want_pe, verbose, want_bf, mice_on_hold, early_stops))
        return return_array
    
    
def FLAME(input_data=False, treatment_column_name='treated',
          outcome_column_name='outcome', adaptive_weights='ridge', alpha=0.1,
          holdout_data=False, repeats=True, verbose=2, want_pe=False, 
          early_stop_iterations=False, stop_unmatched_c=False, 
          early_stop_un_c_frac=False, stop_unmatched_t=False, 
          early_stop_un_t_frac=False, early_stop_pe=False, 
          early_stop_pe_frac=0.01, want_bf=False, early_stop_bf=False, 
          early_stop_bf_frac=0.01, missing_indicator=np.nan, 
          missing_data_replace=0, missing_holdout_replace=0, 
          missing_holdout_imputations=10, missing_data_imputations=0, 
          pre_dame=False, C=0.1):
    """ This function kicks off the FLAME algorithm.
    
    Args:
        See DAME above. The exeption is no weight_array, and the additional:
            
        pre_dame (int, False): Indicates whether to switch to dame and after
            int number of iterations. 
            
    Returns:
        See DAME above.
    """
    
    df, df_holdout = data_cleaning.read_files(input_data, holdout_data)
        
    df = data_cleaning.process_input_file(
        df, treatment_column_name, outcome_column_name, adaptive_weights)

    alpha = data_cleaning.check_parameters(adaptive_weights, df_holdout, df, 
                                           alpha, True, [], C)
    
    df, df_holdout, mice_on_match, mice_on_hold = data_cleaning.check_missings(
        df, df_holdout, missing_indicator, missing_data_replace,
        missing_holdout_replace, missing_holdout_imputations,
        missing_data_imputations, treatment_column_name, outcome_column_name)

    early_stops = data_cleaning.check_stops(
        stop_unmatched_c, early_stop_un_c_frac, stop_unmatched_t,
        early_stop_un_t_frac, early_stop_pe, early_stop_pe_frac, 
        early_stop_bf, early_stop_bf_frac, early_stop_iterations)

    if (mice_on_match == False):
        return_array = flame_algorithm.flame_generic(
            df, treatment_column_name, outcome_column_name, adaptive_weights, 
            alpha, df_holdout, repeats, want_pe, verbose, want_bf, 
            mice_on_hold, early_stops, pre_dame, C)
        
    else:
        # this would mean we need to run mice on the matching data, which means
        # that we have to run flame_generic multiple times
        print("Warning: You have opted to run MICE on the matching dataset. "\
              "This is slow, and not recommended. We recommend that instead,"\
              " you run the algorithm and skip matching on missing data "\
              "points, with the parameter missing_data_replace=2.")
        
        # first we get the imputed datasets
        df_array = flame_dame_helpers.create_mice_dfs(df, mice_on_match)
        return_array = []
        for i in range(len(df_array)):
            return_array.append(flame_algorithm.flame_generic(
                df, treatment_column_name, outcome_column_name, 
                adaptive_weights, alpha, df_holdout, repeats, want_pe, verbose,
                want_bf, mice_on_hold, early_stops, pre_dame, C))
            
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
    if type(mmg_df) == bool and mmg_df == False:
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
        

def te_of_unit(return_df, unit_id, input_data, treatment_column_name, 
               outcome_column_name):
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
    if type(df_mmg) == bool and df_mmg == False:
        print("This unit does not have any matches, so can't find the "\
              "treatment effect")
        return False
    
    if type(input_data) == pd.core.frame.DataFrame:
        df = input_data
    else:
        df = pd.read_csv(return_df)
        
    return query_ate.find(df_mmg, unit_id, df, treatment_column_name, 
                          outcome_column_name)

##### These are fancy versions of the above functions for pretty prints, etc ######

def mmg_and_te_of_unit(return_df, unit_id, input_data, treatment_column_name, 
                       outcome_column_name, return_vals=1):
    """
    Fancy version of above function.
    """
    if return_vals == 0:
        return print_te_and_mmg(return_df, unit_id, input_data, 
                                treatment_column_name, outcome_column_name)
    
    df_mmg = mmg_of_unit(return_df, unit_id, input_data)
    if type(df_mmg) == bool and df_mmg == False:
        print("This unit does not have any matches")
        return False
    
    if type(input_data) == pd.core.frame.DataFrame:
        df = input_data
    else:
        df = pd.read_csv(return_df)
        
    return df_mmg, query_ate.find(df_mmg, unit_id, df, treatment_column_name, 
                                  outcome_column_name)

def print_te_and_mmg(return_df, unit_id, input_data, treatment_column_name, 
                     outcome_column_name):
    """
    Fancy version of above function.
    """
    df_mmg = mmg_of_unit(return_df, unit_id, input_data)
    if type(df_mmg) == bool and df_mmg == False:
        print("This unit does not have any matches")
        return False
    
    te = te_of_unit(return_df, unit_id, input_data, treatment_column_name, 
                    outcome_column_name)
    
    print("This is the Main Matched Group of unit", unit_id, ":")
    print(df_mmg)
    print("This is the treatment effect of unit", unit_id, ":")
    print(te)