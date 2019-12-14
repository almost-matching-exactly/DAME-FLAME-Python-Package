# -*- coding: utf-8 -*-
"""
FLAME Python Package
"""
import numpy as np
import data_cleaning
import flame_algorithm
import flame_dame_helpers


def FLAME(input_data = False,
         treatment_column_name = 'treated', weight_array = [0.25, 0.05, 0.7],
         outcome_column_name='outcome',
         adaptive_weights=False, alpha = 0.1, holdout_data=False,
         repeats=True, verbose=0, want_pe=False, early_stop_iterations=False, 
         early_stop_unmatched_c=False, early_stop_un_c_frac = 0.1, 
         early_stop_unmatched_t=False, early_stop_un_t_frac = 0.1,
         early_stop_pe = False, early_stop_pe_frac = 0.01,
         want_bf=False, early_stop_bf=False, early_stop_bf_frac = 0.01, 
         pre_dame=False, missing_indicator=np.nan, missing_data_replace=0,
         missing_holdout_replace=0, missing_holdout_imputations = 10,
         missing_data_imputations=0):
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

    early_stop_unmatched_c, early_stop_unmatched_t, early_stop_pe, early_stop_bf = data_cleaning.check_stops(
            early_stop_unmatched_c, early_stop_un_c_frac, early_stop_unmatched_t,
            early_stop_un_t_frac, early_stop_pe, early_stop_pe_frac, 
            early_stop_bf, early_stop_bf_frac)
    
    if (mice_on_matching == False):
        return flame_algorithm.flame_generic(df, treatment_column_name, weight_array,
                                outcome_column_name, adaptive_weights, alpha,
                                df_holdout, repeats, want_pe, early_stop_iterations,
                                early_stop_unmatched_c, early_stop_unmatched_t,
                                verbose, want_bf, early_stop_bf, early_stop_pe, 
                                pre_dame, mice_on_holdout)
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
        for i in range(len(df_array)):
            return_array.append(flame_algorithm.flame_generic(df, treatment_column_name, weight_array,
                                outcome_column_name, adaptive_weights, alpha,
                                df_holdout, repeats, want_pe, early_stop_iterations,
                                early_stop_unmatched_c, early_stop_unmatched_t,
                                verbose, want_bf, early_stop_bf, early_stop_pe, 
                                pre_dame, mice_on_holdout))
            
        return return_array
