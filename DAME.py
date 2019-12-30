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
import numpy as np
import data_cleaning
import dame_algorithm
import flame_dame_helpers
import configparser
import sys
import pandas as pd
from data_cleaning import generate_holdout_data, check_stops, check_parameters, process_missing_data


def _DAME(df, df_holdout, dame_config=None):
    """
    This function kicks off the DAME algorithm

    Args:
        input_data: The DataFrame with the data being matched or df. 
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
        alpha (float): This is the alpha for ridge regression 
        holdout_data: DataFrame - if doing an adaptive_weights version, for training
        repeats: Bool, whether or not values for whom a MMG has been found can
            be used again and placed in an auxiliary matched group.
        early_stop_iterations (optional int): If provided, a number of iterations 
            to hard stop the algorithm after.
        early_stop_unmatched_c or early_stop_unmatched_t (optional float, 
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
    # need config
    assert dame_config is not None, "specify DAME configs!"

    # set missing indicator
    missing_indicator = np.nan
    # process inputs
    df = data_cleaning.process_input_file(
        df,
        dame_config["treatment_column_name"],
        dame_config["outcome_column_name"],
        bool(int(dame_config["adaptive_weights"]))
    )

    weights = [float(i) for i in dame_config["weight_array"].split(",")]

    # check parameters
    check_parameters(
        bool(int(dame_config["adaptive_weights"])),
        dame_config["adaptive_weight_strategy"],
        weights,
        df_holdout,
        df,
        float(dame_config["alpha"])
    )

    # check missings
    df, df_holdout, mice_on_matching, mice_on_holdout = process_missing_data(
        df,
        df_holdout,
        dame_config
    )

    # check stops - this requires that you have valid stop values set, even if you
    # are not stopping early
    check_stops(
        float(dame_config["early_stop_un_c_frac"]),
        float(dame_config["early_stop_un_t_frac"]),
        float(dame_config["early_stop_pe_frac"]),
        float(dame_config["early_stop_bf_frac"])
    )

    if mice_on_matching is False:
        return dame_algorithm.algo1(
            df,
            df_holdout,
            dame_config
        )
    else:
        # this would mean we need to run mice on the matching data, which means
        # that we have to run algo1 multiple times
        print("Warning: You have opted to run MICE on the matching dataset. \
              This is slow, and not recommended. We recommend that instead, \
              you run the algorithm and skip matching on missing data points, \
              with the parameter missing_data_replace=2.")

        # first we get the imputed datasets
        df_array = flame_dame_helpers.create_mice_dfs(df, mice_on_matching)
        return_array = []
        for df in df_array:
            return_array.append(
                dame_algorithm.algo1(
                    df,
                    df_holdout,
                    dame_config
                )
            )
        return return_array


def DAME(input_data, holdout_data=None, config_params=None, config_path="dame.conf"):
    """DAME wrapper.

    Args:
        input_data (pandas.DataFrame): input data
        holdout_data (pandas.DataFrame | None): holdout data
        config_params (dict | None): DAME configuration options
        config_path (str): path to DAME configuration file

    Returns:
        result (list[pandas.DataFrame]): DAME results
    """
    # read config
    if config_params is None:
        config = configparser.ConfigParser()
        config.read(config_path)
        config_params = dict(config["params"])

    # process inputs - todo finish this
    if type(input_data) == pd.core.frame.DataFrame:
        df = input_data

    elif input_data is False:
        print("Need to specify either csv file name or pandas data frame in \
              parameter 'input_data'")
        sys.exit(1)
    else:
        try:
            df = pd.read_csv(input_data)
        except ValueError:
            print('Files could not be found')
            sys.exit(1)

    # Now read the holdout data
    if holdout_data is None:
        df_holdout = generate_holdout_data(
            df,
            holdout_frac=float(config_params["holdout_frac"])
        )

    # run DAME routine
    result = _DAME(
        df, df_holdout, dame_config=config_params
    )

    return result
