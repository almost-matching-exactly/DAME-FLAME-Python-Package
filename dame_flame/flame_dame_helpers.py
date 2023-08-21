# -*- coding: utf-8 -*-
"""Helper functions for the flame_algorithm.py and dame_algorithm.py files"""

# author: Neha Gupta, Duke University
# Copyright Duke University 2020
# License: MIT

import numpy as np
import pandas as pd

from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score

from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_squared_error

from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer

def verbose_output(iteration_number, num_matched_groups, num_unmatched_t,
                   num_unmatched, orig_len_df_all, tot_treated, pe,
                   prev_iter_num_unmatched, curr_covar_set):
    '''
    Prints progress of matching algorithm along various metrics
    '''
    print("Completed iteration " + str(iteration_number) + " of matching")
    print("\tNumber of matched groups formed in total: ", num_matched_groups)
    print("\tUnmatched treated units: ", num_unmatched_t, "out of a total of ",
          tot_treated, "treated units")
    print("\tUnmatched control units: ", num_unmatched - num_unmatched_t,
          "out of a total of ", orig_len_df_all - tot_treated, "control units")
    print("\tNumber of matches made this iteration: ",
          prev_iter_num_unmatched - num_unmatched)
    print("\tNumber of matches made so far: ",
          orig_len_df_all - num_unmatched)
    print("\tCovariates dropped so far: ", curr_covar_set)
    print("\tPredictive error of covariate set used to match: ", pe)


def compute_bf(matched_rows, treatment_column_name, df_unmatched):
    '''
    Helper function to compute the balancing factor
    '''

    mg_treated = matched_rows[treatment_column_name].sum()
    mg_control = len(matched_rows) - mg_treated
    available_treated = df_unmatched[treatment_column_name].sum()
    available_control = len(df_unmatched) - available_treated

    if (available_treated != 0 and available_control != 0):
        return (mg_treated/available_treated + mg_control/available_control)
    elif available_treated == 0:
        return mg_control/available_control
    return mg_treated/available_treated


def find_pe_for_covar_set(df_holdout, treatment_column_name,
                          outcome_column_name, s, adaptive_weights,
                          alpha_given):
    '''
    this is a helper function to decide_drop that will find pe of a given s
    '''
    # The iteration and mean of array is only used when doing MICE on holdout
    pe_array = []
    for i in range(len(df_holdout)):


        x_treated, x_control, y_treated, y_control = separate_dfs(
            df_holdout[i], treatment_column_name, outcome_column_name, s)

        # error check. If this is true, we stop matching.
        if type(x_treated) == bool:
            return False

        # binarize holdout dataset if categorical:
        if (adaptive_weights == "decisiontree" or adaptive_weights == "decisiontreeCV"):

            # first binarize non-binary columns in the treated dataset
            bool_cols = bool_cols = [col for col in x_treated
                                     if np.isin(x_treated[col].unique(), [0, 1]).all()]
            non_bool_cols = x_treated.columns.difference(bool_cols)
            if (len(non_bool_cols) != 0):    
                binarized_df = pd.get_dummies(x_treated.loc[:, non_bool_cols].astype(str))
                x_treated = pd.concat([binarized_df, x_treated.loc[:, bool_cols]], axis=1)

            # binarize non-binary columns in the control dataset
            bool_cols = bool_cols = [col for col in x_control
                                     if np.isin(x_control[col].unique(), [0, 1]).all()]
            non_bool_cols = x_control.columns.difference(bool_cols)
            if (len(non_bool_cols) != 0):
                binarized_df = pd.get_dummies(x_control.loc[:, non_bool_cols].astype(str))
                x_control = pd.concat([binarized_df, x_control.loc[:, bool_cols]], axis=1)


        if adaptive_weights in ["ridge", "ridgeCV"]:
            clf = Ridge(alpha=alpha_given)
        elif adaptive_weights in ["decisiontree", "decisiontreeCV"]:
            clf = DecisionTreeRegressor()
        elif adaptive_weights == 0:
            return False
        else:
            clf = adaptive_weights
            # return False

        if adaptive_weights in ["ridgeCV", "decisiontreeCV"]:
            # calculate MSE via cross validation.
            mse_treated = -1*np.mean(cross_val_score(clf, x_treated, y_treated,
                                                     scoring='neg_mean_squared_error',
                                                     cv=5))
            mse_control = -1*np.mean(cross_val_score(clf, x_control, y_control,
                                                     scoring='neg_mean_squared_error',
                                                     cv=5))
        else:
            # Calculate treated MSE
            clf.fit(x_treated, y_treated)
            predicted = clf.predict(x_treated)
            mse_treated = mean_squared_error(y_treated, predicted)

            # Calculate control MSE
            clf.fit(x_control, y_control)
            predicted = clf.predict(x_control)
            mse_control = mean_squared_error(y_control, predicted)

        pe_array.append(mse_treated + mse_control)

    return np.mean(pe_array)

def create_mice_dfs(df_holdout, num_imputes, outcome_col_name):
    '''
    This creates num_imputes number of imputed datasets
    '''
    df_holdout_array = []
    for i in range(num_imputes):
        imp = IterativeImputer(max_iter=10, random_state=i,
                               estimator=DecisionTreeRegressor())
        imp.fit(df_holdout)
        tmp_df = pd.DataFrame(data=np.round(imp.transform(df_holdout)),
                              columns=df_holdout.columns,
                              index=df_holdout.index)
        # convert floats to ints because MICE creates floats
        cols = list(tmp_df.columns)
        cols.remove(outcome_col_name)
        tmp_df[cols] = tmp_df[cols].astype('int64')
        tmp_df[outcome_col_name] = df_holdout[outcome_col_name]
        df_holdout_array.append(tmp_df)

    return df_holdout_array

def separate_dfs(df_holdout, treatment_col_name, outcome_col_name,
                 covs_drop):
    """
    This function serves to create the control/treatment dfs for use
    in the decide_drop functions in flame and in dame.
    """
    #X-treated is the df that has rows where treated col = 1 and
    # all cols except: outcome/treated/the covs being dropped
    x_treated = df_holdout.loc[df_holdout[treatment_col_name] == 1,
                               df_holdout.columns.difference([outcome_col_name,
                                                              treatment_col_name] + list(covs_drop))]

    #X-control is the df that has rows where treated col = 0 and
    # all cols except: outcome/treated/the covs being dropped
    x_control = df_holdout.loc[df_holdout[treatment_col_name] == 0,
                               df_holdout.columns.difference([outcome_col_name,
                                                              treatment_col_name] + list(covs_drop))]

    y_treated = df_holdout.loc[df_holdout[treatment_col_name] == 1,
                               outcome_col_name]

    y_control = df_holdout.loc[df_holdout[treatment_col_name] == 0,
                               outcome_col_name]

    # error check. If this is true, we stop matching.
    if (len(x_treated) == 0 or len(x_control) == 0 or \
        len(y_treated) == 0 or len(y_control) == 0 or \
        len(x_treated.columns) == 0 or len(x_control.columns) == 0):
        return False, False, False, False

    return x_treated, x_control, y_treated, y_control

def stop_iterating(early_stops, df_unmatched, repeats, treat_col_name,
                   orig_len_df_all, h, orig_tot_treated, consider_dropping):
    """
    This function is called during the iterations of DAME and FLAME to see
    if any stopping criteria have been met
    """

    # Iterates while there are units to match to match in
    try:
        if ((early_stops.unmatched_t == True or repeats == False) and
            (1 not in df_unmatched[treat_col_name].values)):
            print(orig_len_df_all - len(df_unmatched), "units matched. "\
                  "We finished with no more treated units to match")
            return True

        if ((early_stops.unmatched_c == True or repeats == False) and
            (0 not in df_unmatched[treat_col_name].values)):
            print(orig_len_df_all - len(df_unmatched), "units matched. "\
                  "We finished with no more control units to match")
            return True

    except TypeError:
        return True
        
    # Hard stop criteria: stop when there are no more units to match
    if (len(df_unmatched) == 0):
        print("All units have been matched.")
        return True

    # Hard stop criteria: exceeded the number of iters user asked for?
    if early_stops.iterations == h:
        print((orig_len_df_all - len(df_unmatched)), "units matched. "\
              "We stopped after iteration", h)
        return True

    # Hard stop criteria: met the threshold of unmatched items to stop?
    if (early_stops.un_t_frac != False or early_stops.un_c_frac != False):
        unmatched_treated = df_unmatched[treat_col_name].sum()
        unmatched_control = len(df_unmatched) - unmatched_treated
        orig_tot_control = orig_len_df_all - orig_tot_treated
        if (early_stops.un_t_frac != False and \
            unmatched_treated/orig_tot_treated < early_stops.un_t_frac):
            print("We stopped the algorithm when ",
                  unmatched_treated/orig_tot_treated, "of the treated "\
                  "units remained unmatched")
            return True

        elif (early_stops.un_c_frac != False and \
            unmatched_control/orig_tot_control < early_stops.un_c_frac):
            print("We stopped the algorithm when ",
                  unmatched_control/orig_tot_control, "of the control "\
                  "units remained unmatched")
            return True

    return False
        
