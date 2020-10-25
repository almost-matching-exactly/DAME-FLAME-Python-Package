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
from . import flame_algorithm
from . import flame_dame_helpers
from . import early_stops

class MatchParent:
    """
    I hope this works ugh.
    """
    def __init__(self, adaptive_weights='ridge', alpha=0.1, repeats=True,
                 verbose=2, early_stop_iterations=False, 
                 stop_unmatched_c=False, early_stop_un_c_frac=False, 
                 stop_unmatched_t=False, early_stop_un_t_frac=False, 
                 early_stop_pe=False, early_stop_pe_frac=0.01, 
                 early_stop_bf=False, early_stop_bf_frac=0.01,
                 missing_indicator=np.nan, missing_data_replace=0, 
                 missing_holdout_replace=0, missing_holdout_imputations=10, 
                 missing_data_imputations=1, want_pe=False, want_bf=False):
        """
        Here, pass in some params and get them set.
        """
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
        self.early_stop_pe_frac = early_stop_pe_frac
        self.early_stop_bf = early_stop_bf
        self.early_stop_bf_frac = early_stop_bf_frac
        self.want_pe = want_pe
        self.want_bf = want_bf
        
    def fit(self, holdout_data=False, treatment_column_name='treated',
            outcome_column_name='outcome', weight_array=False):
        """
        Do the fit
        """
        self.holdout_data = holdout_data
        self.treatment_column_name = treatment_column_name
        self.outcome_column_name = outcome_column_name
        self.weight_array = weight_array
        
class DAME(MatchParent):
    
    def predict(self, input_data):
        """
        ah
        """
        self.input_data, self.holdout_data = data_cleaning.read_files(
            input_data, self.holdout_data)
        
        self.return_array = _DAME(self.input_data.copy(deep=True), 
            self.holdout_data.copy(deep=True),
            self.treatment_column_name, self.weight_array,
            self.outcome_column_name, self.adaptive_weights, self.alpha,
            self.repeats, self.verbose, self.want_pe,
            self.early_stop_iterations, self.stop_unmatched_c,
            self.early_stop_un_c_frac, self.stop_unmatched_t, 
            self.early_stop_un_t_frac, self.early_stop_pe, 
            self.early_stop_pe_frac, self.want_bf, self.early_stop_bf, 
            self.early_stop_bf_frac, self.missing_indicator, 
            self.missing_data_replace, self.missing_holdout_replace, 
            self.missing_holdout_imputations, self.missing_data_imputations)   
        
        
        self.bf_each_iter = None
        self.pe_each_iter = None
        # in the non-mice case:
        if (self.missing_data_replace != 3):
            self.df_units_and_covars_matched = self.return_array[0]
            self.groups_per_unit = self.df_units_and_covars_matched['weights']
            self.df_units_and_covars_matched = self.df_units_and_covars_matched.drop(columns = ['weights'])
            self.units_per_group = self.return_array[1]
            if (self.want_pe == True):
                self.pe_each_iter = self.return_array[2]
            if (self.want_bf == True):
                self.bf_each_iter = self.return_array[-1]
        else:
            # in the mice case:
            array_of_dfs = []
            array_of_groups_per_unit = []
            for arr in self.return_array:
                temp_df = self.return_array[0]
                array_of_groups_per_unit.append(temp_df['weights'])
                array_of_dfs.append(temp_df.drop(columns=['weights']))
            self.groups_per_unit = array_of_groups_per_unit
            self.df_units_and_covars_matched = array_of_dfs     
            
        return self.df_units_and_covars_matched

class FLAME(MatchParent):
    
    def predict(self, input_data, pre_dame=False, C=0.1):
        """
        fill me in
        """
        
        self.input_data, self.holdout_data = data_cleaning.read_files(
            input_data, self.holdout_data)
        
        self.return_array = _FLAME(self.input_data.copy(deep=True), 
            self.holdout_data.copy(deep=True), self.treatment_column_name, 
            self.weight_array,self.outcome_column_name, self.adaptive_weights, 
            self.alpha, self.repeats, self.verbose, self.want_pe,
            self.early_stop_iterations, self.stop_unmatched_c,
            self.early_stop_un_c_frac, self.stop_unmatched_t, 
            self.early_stop_un_t_frac, self.early_stop_pe, 
            self.early_stop_pe_frac, self.want_bf, self.early_stop_bf, 
            self.early_stop_bf_frac, self.missing_indicator, 
            self.missing_data_replace, self.missing_holdout_replace, 
            self.missing_holdout_imputations, self.missing_data_imputations,
            pre_dame, C)   
        
        
        self.bf_each_iter = None
        self.pe_each_iter = None
        # in the non-mice case:
        if (self.missing_data_replace != 3 and pre_dame==False):
            self.df_units_and_covars_matched = self.return_array[0]
            self.groups_per_unit = self.df_units_and_covars_matched['weights']
            self.df_units_and_covars_matched = self.df_units_and_covars_matched.drop(columns = ['weights'])
            self.units_per_group = self.return_array[1]
            if (self.want_pe == True):
                self.pe_each_iter = self.return_array[2]
            if (self.want_bf == True):
                self.bf_each_iter = self.return_array[-1]
        else:
            # in the mice case or pre_dame case, we have multiple return vals
            array_of_dfs = []
            array_of_groups_per_unit = []
            for arr in self.return_array:
                temp_df = self.return_array[0]
                array_of_groups_per_unit.append(temp_df['weights'])
                array_of_dfs.append(temp_df.drop(columns=['weights']))
            self.groups_per_unit = array_of_groups_per_unit
            self.df_units_and_covars_matched = array_of_dfs     
            
        return self.df_units_and_covars_matched
    

def _DAME(df, df_holdout, treatment_column_name='treated', weight_array=False,
         outcome_column_name='outcome', adaptive_weights='ridge', alpha=0.1,
         repeats=True, verbose=2, want_pe=False, 
         early_stop_iterations=False, stop_unmatched_c=False, 
         early_stop_un_c_frac=False, stop_unmatched_t=False, 
         early_stop_un_t_frac=False, early_stop_pe=False, 
         early_stop_pe_frac=0.01, want_bf=False, early_stop_bf=False, 
         early_stop_bf_frac=0.01, missing_indicator=np.nan, 
         missing_data_replace=0, missing_holdout_replace=0, 
         missing_holdout_imputations=10, missing_data_imputations=1):
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
    
    
def _FLAME(df, df_holdout, treatment_column_name='treated', weight_array=False,
          outcome_column_name='outcome', adaptive_weights='ridge', alpha=0.1, 
          repeats=True, verbose=2, want_pe=False, 
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
        See DAME above. The exeption is no weight_array, and the additional 
        params below:
            
        pre_dame (int, False): Indicates whether to switch to dame and after
            int number of iterations. 
        C (float, 0.1): The tradeoff between PE and BF in computing MQ

            
    Returns:
        See DAME above.
    """
            
    df = data_cleaning.process_input_file(
        df, treatment_column_name, outcome_column_name, adaptive_weights)

    alpha = data_cleaning.check_parameters(adaptive_weights, df_holdout, df, 
                                           alpha, True, weight_array, C)
    
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
            df, treatment_column_name, weight_array, outcome_column_name, 
            adaptive_weights, alpha, df_holdout, repeats, want_pe, verbose, 
            want_bf, mice_on_hold, early_stops, pre_dame, C)
        
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
                df, treatment_column_name, weight_array, outcome_column_name, 
                adaptive_weights, alpha, df_holdout, repeats, want_pe, verbose,
                want_bf, mice_on_hold, early_stops, pre_dame, C))
            
    return return_array

