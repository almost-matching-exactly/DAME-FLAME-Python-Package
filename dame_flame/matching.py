# -*- coding: utf-8 -*-
"""
DAME and FLAME Matching Methods for Causal Inference. Starts matching methods.
"""
# author: Neha Gupta, Duke University
# Copyright Duke University 2020
# License: MIT

import numpy as np
import pandas as pd
from . import data_cleaning
from . import dame_algorithm
from . import flame_algorithm
from . import flame_dame_helpers

class MatchParent:
    """ Matching via DAME or FLAME algorithms

    MatchParent aims to create and object for matching a given dataset.
    Read more in the documentation User Guide:
    https://almost-matching-exactly.github.io/DAME-FLAME-Python-Package/

    Parameters
    -----------
    adaptive_weights (bool, str): Weight dropping method. False, 'ridge',
        'decisiontree', 'ridgeCV', or 'decisiontreeCV'.
    alpha (float): This is the alpha for ridge regression. We use the
        scikit package for ridge regression, so it is "regularization
        strength". Larger values specify stronger regularization.
        Must be positive float.
    repeats (bool): whether values for whom a MMG has been found can
        be used again and placed in an auxiliary matched group.
    verbose (default: 2): If 1, provides iteration num, if 2 provides
        iteration number and number of units left to match on every 10th
        iter, if 3 does this print on every iteration. If 0, nothing.
    early_stop_iterations (optional int): If provided, a number of iters
        to hard stop the algorithm after.
    stop_unmatched_c, stop_unmatched_t (bools): specifies whether
        the algorithm stops when there are no units remaining to match
    early_stop_un_c_frac, early_stop_un_t_frac (optional float,
        from 0.0 - 1.0): If provided, a fraction of unmatched control/
        treatment units. When threshold met, hard stop the algo.
    early_stop_pe: Whether the covariate set chosen to match
        on has a pe lower than the parameter early_stop_pe_val, at
        which point the algorithm will stop.
    missing_holdout_replace (0,1,2): default 0.
        if 0, assume no missing holdout data and proceed
        if 1, drop all missing_indicator values from holdout dataset
        if 2, do mice on holdout dataset for missing_holdout_imputations
        number of imputations
    missing_data_replace (0,1,2,3): default 0.
        if 0, assume no missing data in matching data and proceed
        if 1, drop all missing_indicator values from matching data
        if 2, replace all missing_indicator values with unique large vals
        so they essentially get skipped in the matching
        if 3, do mice on matching dataset for missing_data_imputations
        number of imputations.
    missing_holdout_imputations: If missing_holdout_replace=2, the number
        of imputations on the holdout set.
    missing_data_imputations: If missing_data_replace=3, the number of
        imputations on the matching set.
    missing_indicator: This is the character/number/np.nan that indicates
        missing vals in the holdout/matching data.
    want_pe: whether the output of the algorithm will include the
        predictive error of the covariate sets matched on in each iteration
    want_bf: whether the output will include the balancing factor of each
        iteration.
    """
    def __init__(self, adaptive_weights='ridge', alpha=0.1, repeats=True,
                 verbose=2, early_stop_iterations=float('inf'),
                 stop_unmatched_c=False, early_stop_un_c_frac=False,
                 stop_unmatched_t=False, early_stop_un_t_frac=False,
                 early_stop_pe=0.05,
                 missing_indicator=np.nan, missing_data_replace=0,
                 missing_holdout_replace=0, missing_holdout_imputations=10,
                 missing_data_imputations=1, want_pe=False, want_bf=False):

        self.adaptive_weights = adaptive_weights
        self.alpha = alpha
        self.repeats = repeats
        self.verbose = verbose
        self.missing_indicator = missing_indicator
        self.missing_data_replace = missing_data_replace
        self.missing_holdout_replace = missing_holdout_replace
        self.missing_holdout_imputations = missing_holdout_imputations
        self.missing_data_imputations = missing_data_imputations
        self.early_stop_iterations = early_stop_iterations
        self.stop_unmatched_c = stop_unmatched_c
        self.early_stop_un_c_frac = early_stop_un_c_frac
        self.stop_unmatched_t = stop_unmatched_t
        self.early_stop_un_t_frac = early_stop_un_t_frac
        self.early_stop_pe = early_stop_pe
        self.want_pe = want_pe
        self.want_bf = want_bf

    def fit(self, holdout_data=False, treatment_column_name='treated',
            outcome_column_name='outcome', weight_array=False):
        """
        Save model data that will be used to fit the matching method.

        Parameters
        ----------
        holdout_data : {string, dataframe, float, False }, default = False
            This is the holdout dataset. If a string is given, that should be
            the location of a CSV file to input. If a float between 0.0 and 1.0
            is given, that corresponds the percent of the input dataset to
            randomly select for holdout data. If False, the holdout data is
            equal to the entire input data.
        treatment_column_name : string, default="treated"
            the name of the column with a binary indicator for whether a row is
            a treatment or control unit.
        outcome_column_name : string, default="outcome"
            This is the name of the column with the outcome variable of each
            unit.
        weight_array : array, optional
            If adaptive_weights = False, these are the weights to the
            covariates in input_data, for the non-adaptive version of DAME.
            Must sum to 1. In this case, we do not use machine learning for the
            weights, they are manually entered as weight_array.

        """
        self.holdout_data = holdout_data
        self.treatment_column_name = treatment_column_name
        self.outcome_column_name = outcome_column_name
        self.weight_array = weight_array

class DAME(MatchParent):
    '''
    This is the class used for the DAME algorithm
    '''
    def predict(self, input_data):
        """
        Performs match and returns matched data.

        Parameters
        ----------
        input_data: {string, dataframe}, required parameter
            The dataframe on which to perform the matching, or the location of
            the CSV with the dataframe
        """
        self.input_data, self.holdout_data = data_cleaning.read_files(
            input_data, self.holdout_data)

        return_array = _DAME(self.input_data.copy(deep=True),
            self.holdout_data.copy(deep=True),
            self.treatment_column_name, self.weight_array,
            self.outcome_column_name, self.adaptive_weights, self.alpha,
            self.repeats, self.verbose, self.want_pe,
            self.early_stop_iterations, self.stop_unmatched_c,
            self.early_stop_un_c_frac, self.stop_unmatched_t,
            self.early_stop_un_t_frac, self.early_stop_pe,
            self.want_bf,
            self.missing_indicator,
            self.missing_data_replace, self.missing_holdout_replace,
            self.missing_holdout_imputations, self.missing_data_imputations)

        self.bf_each_iter = None
        self.pe_each_iter = None

        # in the non-mice case:
        if (self.missing_data_replace != 3):
            self.df_units_and_covars_matched = return_array[0]
            self.groups_per_unit = self.df_units_and_covars_matched['weights']
            self.df_units_and_covars_matched = self.df_units_and_covars_matched.drop(columns = ['weights'])
            self.units_per_group = return_array[1]
            if self.want_pe:
                self.pe_each_iter = return_array[2]
            if self.want_bf:
                self.bf_each_iter = return_array[-1]
        else:
            # in the mice case:
            array_of_dfs = []
            array_of_groups_per_unit = []
            array_of_units_per_group = []
            for arr in return_array:
                temp_df = arr[0]
                array_of_groups_per_unit.append(temp_df['weights'])
                array_of_dfs.append(temp_df.drop(columns=['weights']))
                array_of_units_per_group.append(arr[1])
            self.groups_per_unit = array_of_groups_per_unit
            self.df_units_and_covars_matched = array_of_dfs
            self.units_per_group = array_of_units_per_group

        return self.df_units_and_covars_matched

class FLAME(MatchParent):
    '''
    The class used for the FLAME algorithm
    '''
    def predict(self, input_data, pre_dame=float('inf'), C=0.1):
        """
        Performs match and returns matched data.

        Parameters
        ----------
        input_data: {string, dataframe}, required parameter
            The dataframe on which to perform the matching, or the location of
            the CSV with the dataframe
        pre_dame (int, float): Indicates whether to switch to dame after
            int number of iterations. If float('inf') (default), only run FLAME.
        C (float, 0.1): The tradeoff between PE and BF in computing MQ
        """
        self.input_data, self.holdout_data = data_cleaning.read_files(
            input_data, self.holdout_data)

        return_array = _FLAME(self.input_data.copy(deep=True),
            self.holdout_data.copy(deep=True), self.treatment_column_name,
            self.weight_array,self.outcome_column_name, self.adaptive_weights,
            self.alpha, self.repeats, self.verbose, self.want_pe,
            self.early_stop_iterations, self.stop_unmatched_c,
            self.early_stop_un_c_frac, self.stop_unmatched_t,
            self.early_stop_un_t_frac, self.early_stop_pe,
            self.want_bf, self.missing_indicator,
            self.missing_data_replace, self.missing_holdout_replace,
            self.missing_holdout_imputations, self.missing_data_imputations,
            pre_dame, C)

        self.bf_each_iter = None
        self.pe_each_iter = None
		
        # in the non-mice case:
        if self.missing_data_replace != 3 and pre_dame == float('inf'):
            self.df_units_and_covars_matched = return_array[0]
            self.groups_per_unit = self.df_units_and_covars_matched['weights']
            self.df_units_and_covars_matched = self.df_units_and_covars_matched.drop(columns=['weights'])
            self.units_per_group = return_array[1]
            if self.want_pe:
                self.pe_each_iter = return_array[2]
            if self.want_bf:
                self.bf_each_iter = return_array[-1]

        if (self.missing_data_replace != 3 and pre_dame == float('inf')):
            self.df_units_and_covars_matched = return_array[0]
            self.groups_per_unit = self.df_units_and_covars_matched['weights']
            self.df_units_and_covars_matched = self.df_units_and_covars_matched.drop(columns = ['weights'])
            self.units_per_group = return_array[1]
            if (self.want_pe == True):
                self.pe_each_iter = return_array[2]
            if (self.want_bf == True):
                self.bf_each_iter = return_array[-1]

        elif pre_dame < float('inf'):

            # the first few items all look the same, then the last item is from dame
            self.df_units_and_covars_matched = return_array[0]
            # self.df_units_and_covars_matched = self.df_units_and_covars_matched.append(return_array[-1][0], sort=True)
            self.df_units_and_covars_matched = pd.concat([self.df_units_and_covars_matched, return_array[-1][0]])

            if self.repeats == True:
                # we have to aggregate the indexes appearing more than once,
                # those are the ones which were matched units in both dame and flame:

                df_wrepeats = self.df_units_and_covars_matched
                # this is a df without repeat indexes
                df_no_repeats = df_wrepeats[~df_wrepeats.index.duplicated(keep='first')].copy()

                #iterate through repeat indexes and sum weight column
                matched_twice_ind = df_wrepeats[df_wrepeats.index.duplicated()].index.unique()
                for index in matched_twice_ind:
                    df_no_repeats.loc[index, 'weights'] = df_wrepeats.loc[index].copy()['weights'].sum()

                self.df_units_and_covars_matched = df_no_repeats

            self.df_units_and_covars_matched.replace(np.nan, "*")
            self.groups_per_unit = self.df_units_and_covars_matched['weights']

            self.df_units_and_covars_matched = self.df_units_and_covars_matched.drop(columns = ['weights'])
            self.units_per_group = return_array[1]
            self.units_per_group += return_array[-1][1]
            if (self.want_pe == True):
                self.pe_each_iter = return_array[2]
                self.pe_each_iter += return_array[-1][2]
            if (self.want_bf == True):
                self.bf_each_iter = return_array[-2]
                self.bf_each_iter += return_array[-1][-2]

        else:
            # This is the mice case, where we have multiple return values.
            # We leave those as arrays.
            self.df_units_and_covars_matched = []
            self.groups_per_unit = []
            self.df_units_and_covars_matched = []
            self.units_per_group = []
            self.pe_each_iter = []
            self.bf_each_iter = []
            for return_val in return_array:
                self.df_units_and_covars_matched.append(return_val[0].drop(columns = ['weights']))
                self.groups_per_unit.append(return_val[0]['weights'])
                self.units_per_group.append(return_val[1])
                if self.want_pe:
                    self.pe_each_iter.append(return_val[2])
                if self.want_bf:
                    self.bf_each_iter.append(return_val[-1])


        return self.df_units_and_covars_matched


def _DAME(df, df_holdout, treatment_column_name='treated', weight_array=False,
          outcome_column_name='outcome', adaptive_weights='ridge', alpha=0.1,
          repeats=True, verbose=2, want_pe=False,
          early_stop_iterations=float('inf'), stop_unmatched_c=False,
          early_stop_un_c_frac=False, stop_unmatched_t=False,
          early_stop_un_t_frac=False, early_stop_pe=0.05,
          want_bf=False, missing_indicator=np.nan,
          missing_data_replace=0, missing_holdout_replace=0,
          missing_holdout_imputations=10, missing_data_imputations=1):
    """ Accepts user input, validates, error-checks, calls DAME algorithm.

    Args:
        See description in MatchParent class above.

    Returns:
        return_df: df of units with the column values of their main matched
            group, with "*"s in place for the columns not in their MMG;
            includes a unit weights column which indicates the number of times
            each unit was matched
        MG_units: list of unit ids for every matched group
        pe_array: If want_pe is true, then the PE values of each match
        bf_array: If want_bf is true, then the BF values of each match

    Raises:
        Exception: An error occurred in the data_cleaning.py file.
    """

    df = data_cleaning.process_input_file(df, treatment_column_name, 
                                          outcome_column_name)

    data_cleaning.check_parameters(adaptive_weights, df_holdout, df,
                                   alpha, False, weight_array)

    df, df_holdout, mice_on_match, mice_on_hold = data_cleaning.check_missings(
        df, df_holdout, missing_indicator, missing_data_replace,
        missing_holdout_replace, missing_holdout_imputations,
        missing_data_imputations, treatment_column_name, outcome_column_name,
        adaptive_weights)

    early_stops = data_cleaning.check_stops(
        stop_unmatched_c, early_stop_un_c_frac, stop_unmatched_t,
        early_stop_un_t_frac, early_stop_pe, 
        early_stop_iterations)

    if not mice_on_match:
        return dame_algorithm.algo1(
            df, treatment_column_name, weight_array, outcome_column_name,
            adaptive_weights, alpha, df_holdout, repeats, want_pe, verbose,
            want_bf, mice_on_hold, early_stops)

    # if the 'if' condition is not true, this would mean we need to run mice on
    # the matching data, which means that we have to run algo1 multiple times
    print("Warning: You have opted to run MICE on the matching dataset. "\
          "This is slow, and not recommended. We recommend that instead,"\
          " you run the algorithm and skip matching on missing data "\
              "points, with the parameter missing_data_replace=2.")

    # first we get the imputed datasets
    df_array = flame_dame_helpers.create_mice_dfs(df, mice_on_match,
                                                  outcome_column_name)
    return_array = []
    for i in range(len(df_array)):
        return_array.append(dame_algorithm.algo1(
            df_array[i], treatment_column_name, weight_array,
            outcome_column_name, adaptive_weights, alpha, df_holdout,
            repeats, want_pe, verbose, want_bf, mice_on_hold, early_stops))
    return return_array


def _FLAME(df, df_holdout, treatment_column_name='treated', weight_array=False,
           outcome_column_name='outcome', adaptive_weights='ridge', alpha=0.1,
           repeats=True, verbose=2, want_pe=False,
           early_stop_iterations=float('inf'), stop_unmatched_c=False,
           early_stop_un_c_frac=False, stop_unmatched_t=False,
           early_stop_un_t_frac=False, early_stop_pe=0.05,
           want_bf=False,
           missing_indicator=np.nan,
           missing_data_replace=0, missing_holdout_replace=0,
           missing_holdout_imputations=10, missing_data_imputations=0,
           pre_dame=float('inf'), C=0.1):
    """ This function kicks off the FLAME algorithm.

    Args:
        See DAME above. The exeption is no weight_array, and the additional
        params below:

        pre_dame (int, float): Indicates whether to switch to dame and after
            int number of iterations. A value of float('inf') (default) means only FLAME is run.
        C (float, 0.1): The tradeoff between PE and BF in computing MQ


    Returns:
        See DAME above.
    """

    df = data_cleaning.process_input_file(
        df, treatment_column_name, outcome_column_name)

    data_cleaning.check_parameters(
        adaptive_weights, df_holdout, df, alpha, True, weight_array, C)

    df, df_holdout, mice_on_match, mice_on_hold = data_cleaning.check_missings(
        df, df_holdout, missing_indicator, missing_data_replace,
        missing_holdout_replace, missing_holdout_imputations,
        missing_data_imputations, treatment_column_name, outcome_column_name,
        adaptive_weights)

    early_stops = data_cleaning.check_stops(
        stop_unmatched_c, early_stop_un_c_frac, stop_unmatched_t,
        early_stop_un_t_frac, early_stop_pe, 
        early_stop_iterations)

    if not mice_on_match:
        return_array = flame_algorithm.flame_generic(
            df, treatment_column_name, weight_array, outcome_column_name,
            adaptive_weights, alpha, df_holdout, repeats, want_pe, verbose,
            want_bf, mice_on_hold, early_stops, pre_dame, C)

    else:
        # this would mean we need to run mice on the matching data, which means
        # that we have to run flame_generic multiple times
        if pre_dame < float('inf'):
            raise Exception("Invalid Input Error. At this time, we do not "\
                            "allow users to run the hybrid algorithm while "\
                            "running MICE on the matching dataset.")

        print("Warning: You have opted to run MICE on the matching dataset. "\
              "This is slow, and not recommended. We recommend that instead,"\
              " you run the algorithm and skip matching on missing data "\
              "points, with the parameter missing_data_replace=2.")

        # first we get the imputed datasets
        df_array = flame_dame_helpers.create_mice_dfs(df, mice_on_match,
                                                      outcome_column_name)

        return_array = []
        for i in range(len(df_array)):
            return_array.append(flame_algorithm.flame_generic(
                df_array[i], treatment_column_name, weight_array, outcome_column_name,
                adaptive_weights, alpha, df_holdout, repeats, want_pe, verbose,
                want_bf, mice_on_hold, early_stops, pre_dame, C))

    return return_array
