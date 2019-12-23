# -*- coding: utf-8 -*-
"""

@author: Neha
"""
import numpy as np
import sys
import math


def assert_positive_less_than_one(value, error_message):
    """Helper for checking that a value is 0<v<1."""
    assert value > 0 and value < 1, error_message


def generate_holdout_data(input_data, holdout_frac=0.10):
    """Generates holdout data based on input data.
    Args:
        input_data (pandas.DataFrame): input data

    Returns:
         (pandas.DataFrame): holdout data
    """
    assert_positive_less_than_one(
        holdout_frac,
        "invalid holdout fraction specified"
    )
    return input_data.sample(frac=holdout_frac)


def check_stops(
        early_stop_un_c_frac,
        early_stop_un_t_frac, early_stop_pe_frac,
        early_stop_bf_frac):
    """
    This function checks the parameters passed to DAME/FLAME relating to early
    stopping.

    Args:
        early_stop_un_c_frac (float)
        early_stop_un_t_frac (float)
        early_stop_pe_frac (float)
        early_stop_bf_frac (float)

    Returns:
        None
    """
    assert_positive_less_than_one(
        early_stop_un_t_frac,
        "invalid early_top_un_t_frac specified"
    )

    assert_positive_less_than_one(
        early_stop_un_c_frac,
        "invalid early_stop_un_c_frac specified"
    )

    assert_positive_less_than_one(
        early_stop_pe_frac,
        "invalid early_stop_pe_frac specified"
    )

    assert_positive_less_than_one(
        early_stop_bf_frac,
        "invalid early_stop_bf_frac specified"
    )


def check_parameters(adaptive_weights, weight_array, df_holdout, df,
                     alpha):
    '''
    This function processes the parameters that were passed to DAME/FLAME
    that aren't directly the input file or related to stop_criteria. 
    '''

    if adaptive_weights is False:

        # Confirm that weight array has the right number of values in it
        # Subtracting 2 because one col is the treatment and one is outcome.
        assert len(weight_array) == (len(df.columns) - 2), \
            "Weight array must be of length {0}".format(len(df.columns) - 1)
        # I do this weird operation instead of seeing if it equals one
        # to avoid floatig point addition errors that can occur.
        assert abs(sum(weight_array) - 1.0) < 0.001, \
            "Weight array values must sum to 1.0"

    else:
        # make sure that the alpha is valid if it's a ridge regression.
        assert_positive_less_than_one(
            alpha,
            "alpha must be between 0 and 1"
        )
        # make sure that adaptive_weights is a valid value.
        assert adaptive_weights in ["ridge", "decision_tree"], \
            "Adaptive weights must be ridge or decision tree"

        # make sure the two dfs have the same number of columns first:
        if (len(df.columns) != len(df_holdout.columns)):
            print('Invalid input error. The holdout and main dataset \
                  must have the same number of columns')
            sys.exit(1)
        # make sure that the holdout columns match the df columns.
        if (set(df_holdout.columns) != set(df.columns)):
            # they don't match
            print('Invalid input error. The holdout and main dataset \
                  must have the same columns')
            sys.exit(1)


def replace_unique_large(df, treatment_column_name, outcome_column_name,
                         missing_indicator):
    ''' (helper)
    This function replaces missing values from the df with unique large values
    could possibly clean this up later
    '''
    max_val = df.max().max()
    # now we replace all of the missing_indicators with unique large vals
    # that are larger than max_val. 
    for col in df.columns:
        if col != treatment_column_name and col != outcome_column_name:
            for item_num in range(len(df[col])):
                if math.isnan(missing_indicator) == False:
                    if df[col][item_num] == missing_indicator:
                        df.loc[item_num, col] = max_val + 1
                        max_val += 1
                else:
                    # Have to do them separately because nan == nan is false always.
                    if math.isnan(df[col][item_num]) == True:
                        df.loc[item_num, col] = max_val + 1
                        max_val += 1
                    
    return df

def drop_missing(df, treatment_column_name, outcome_column_name, missing_indicator):
    ''' 
    helper, this function drops rows that have missing_indicator in any of the cols
    '''
    
    if math.isnan(missing_indicator) == True:
        # either the missing indicator is already NaN and we just drop those rows
        df = df.dropna()
    else:
        # but if its not NaN, switch missing_indicator with nan and then drop
        df = df.replace(missing_indicator, np.nan)
        df = df.dropna()

    return df


def process_missing_data(df, df_holdout, dame_config):
    '''
    This function deals with all the missing data related stuff
    '''
    mice_on_matching = False
    mice_on_holdout = False
    print("hi: ", df.isnull().values.any())
    if missing_data_replace == 0 and df.isnull().values.any() == True:
        print('There is missing data in this dataset. The default missing \
              data handling is being done, so we are not matching on \
              any missing values in the matching set')
        missing_data_replace = 2
        # TODO: iterate through all the columns and check for non-integer values
        # and then replace them with nan if needed. 
        # df['hi'] = pd.to_numeric(df['hi'], errors='coerce')

    if missing_data_replace == 1:
        df = drop_missing(df, treatment_column_name, outcome_column_name,
                          missing_indicator)

    if missing_data_replace == 2:
        # so replacing with large unique values will only work if columns 
        # are in order!!

        df = replace_unique_large(df, treatment_column_name, outcome_column_name,
                             missing_indicator)
        
        
        # Reorder if they're not in order:
        df = df.loc[:, df.max().sort_values(ascending=True).index]
        
    if missing_data_replace == 3:
        # this means do mice but only if theres something actually missing. 
        df = df.replace(missing_indicator, np.nan)
        if df.isnull().values.any() == True:
            mice_on_matching = missing_data_imputations
    
    if missing_holdout_replace == 0 and df_holdout.isnull().values.any() == True:
        print('There is missing data in this dataset. The default missing \
              data handling is being done, so we are running MICE on 10 \
              imputed holdout datasets')
        missing_holdout_replace = 2
    
    if missing_holdout_replace == 1:
        df_holdout = drop_missing(df_holdout, treatment_column_name, 
                                  outcome_column_name, missing_indicator)
        
    if missing_holdout_replace == 2:
        # this means do mice ugh lol. 
        df_holdout = df_holdout.replace(missing_indicator, np.nan)
        print('df_holdout')
        # but if there is actually nothing missing in the dataset, then dont
        # need to do this. 
        if df_holdout.isnull().values.any() == True:
            print("I should be true")
            mice_on_holdout = missing_holdout_imputations
    
    return df, df_holdout, mice_on_matching, mice_on_holdout

def process_input_file(df, treatment_column_name, outcome_column_name, adaptive_weights):
    '''
    This function processes the parameters passed to DAME/FLAME that are 
    directly the input file.
    
    '''
    
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
        
    if adaptive_weights == False:
        # Ensure that the columns are sorted in order: binary, tertary, etc
        max_column_size = 1
        for col_name in df.columns:
            if (col_name != treatment_column_name) and (col_name != outcome_column_name):
                # Todo: before, this was df[col_name].unique().max(), which I removed when it didnt work
                # this seems to work, but I wonder if it's a happy accident
                # because, https://stackoverflow.com/questions/21319929/how-to-determine-whether-a-pandas-column-contains-a-particular-value
                if df[col_name].max() >= max_column_size:
                    max_column_size = df[col_name].max()
                else:
                    print('Invalid input error. Dataframe column size must be in \
                          increasing order from left to right.')
                    sys.exit(1)
    
    else:
        # Reorder if they're not in order:
        df = df.loc[:, df.max().sort_values(ascending=True).index]
                
        
        

    return df