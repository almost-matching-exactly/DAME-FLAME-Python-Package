# -*- coding: utf-8 -*-
""" The main place where the DAME algorithm happens"""
# author: Neha Gupta, Duke University
# Copyright Duke University 2020
# License: MIT

import numpy as np
import pandas as pd
from . import grouped_mr
from . import generate_new_active_sets
from . import flame_dame_helpers



def decide_drop(all_covs, active_covar_sets, weights, adaptive_weights,
                treatment_column_name, outcome_column_name, df_holdout,
                alpha_given):
    """ This is a helper function to Algorithm 1 in the paper.

    Args:
        all_covs: This is an array of just the cov column names.
            Not including treat/outcome
        active_covar_sets: A set of frozensets, representing all the active
            covar sets
        weights: This is the weight array provided by the user
        adaptive_weights: This is the T/F provided by the user indicating
            whether to run ridge regression to decide who to drop.
        treatment_column_name (str): name of treatment column in df
        outcome_column_name (str): name of outcome column in df
        df_holdout: The cleaned, user-provided dataframe with all rows/columns.
            There are no changes made to this throughout the code. Used only in
            testing/training for adaptive_weights version.
    """
    curr_covar_set = set()
    best_pe = float("inf")
    if not adaptive_weights:
        # We iterate through all active covariate sets and find the total
        # weight of each . For each possible covariate set, temp_weight counts
        # the total weight of the covs that are going to get used in the match,
        # or the ones *not* in that possible cov set.
        max_weight = 0
        for s in active_covar_sets: # s is a set to consider dropping
            temp_weight = 0
            for cov_index in range(len(all_covs)):  # iter through all covars
                if all_covs[cov_index] not in s:
                    # if an item not in s, add weight. finding impact of drop s
                    temp_weight += weights[cov_index]
            if temp_weight >= max_weight:
                max_weight = temp_weight
                curr_covar_set = s # This is the items we will drop, that will
                # not get used in the match.
        best_pe = max_weight

    else:
        # Iterate through all of the active_covar_sets and drop one at a time,
        # and drop the one with the highest match quality score
        for s in active_covar_sets:
            # S is the frozenset of covars we drop. We try dropping each one
            PE = flame_dame_helpers.find_pe_for_covar_set(df_holdout,
                                                          treatment_column_name,
                                                          outcome_column_name, s, adaptive_weights,
                                                          alpha_given)
            # error check. PE can be float(0), but not denote error
            if not PE and type(PE) == bool:
                return False, False

            # Use the smallest PE as the covariate set to drop.
            if PE < best_pe:
                best_pe = PE
                curr_covar_set = s

    return curr_covar_set, best_pe


def algo1(df_all, treatment_column_name="T", weight_array=[],
          outcome_column_name="outcome", adaptive_weights=False, alpha=0.1,
          df_holdout="", repeats=True, want_pe=False, verbose=0,
          want_bf=False, missing_holdout_replace=False, early_stops=False):
    """This function does Algorithm 1 in the paper.

    Args:
        df_all: The cleaned, user-provided dataframe with all rows/columns.
            There are no changes made to this throughout the code when the
            parameter "repeats" is True. In the DAME paper, this is called 'D'.
        treatment_column_name: As provided by the user, this indicates the name
            of the column that contains the binary indicator for whether each
            row is a treatment group or not.
        weight_array: As provided by the user, array of weights of all covariates
            that are in df_all.
        outcome_column_name: As provided by the user, this indicates the name
            of the column that contains the outcome values.
        adaptive_weights: Provided by the user, this is true if decide to drop
            weights based on a ridge regression on hold-out training set
            or false (default) if decide to drop weights
            based on the weights given in the weight_array
        alpha (float): for ridge regression.
        df_holdout: The array of cleaned, user-provided dataframe with all
            rows/columns. There are no changes made to this throughout the
            code. Used only in testing/training for adaptive_weights version.
            Size 1 with 1 array if not doing MICE on holdout dataset.
        repeats (bool): Provided by user, whether or not values for whom a MMG
            has been found can be used again and placed in an auxiliary group.
        want_pe (bool): Whether or not we want predictive error of each match
        want_bf (bool): Whether to compute and output the balancing factor of
            each group.
        missing_holdout_replace (bool/float): Default false. If int, the number of
            imputations that MICE needs to do on the holdout dataset, which
            has NaNs in it that need to be replaced.
        early_stops (type EarlyStop): This is all of the possible stop criteria

    Returns:
        return_df: df of units with the column values of their main matched
            group, with "*"s in place for the columns not in their MMG;
            includes a unit weights column which indicates the number of times
            each unit was matched
        MG_units: list of unit ids for every matched group
    """

    # Initialize variables. These are all moving/temporary throughout algo
    all_covs = df_all.columns.tolist()
    all_covs.remove(treatment_column_name) # This is J in the paper
    all_covs.remove(outcome_column_name)
    df_unmatched = df_all.copy(deep=True) # This is df_h in the paper

    # Initialize return values
    return_pe = []
    return_bf = []
    MG_units = [] # list of unit ids for each matched group
    # weights indicates the number of times each unit appears in a group
    weights = pd.DataFrame(np.zeros(shape=(len(df_all.index), 1)),
                           columns=['weights'],
                           index=df_all.index)
    return_matches = pd.DataFrame(columns=all_covs, index=df_all.index)

    # Initialize variables used in checking stopping criteria
    orig_len_df_all = len(df_all) # Need this bc of case where repeats=False
    orig_tot_treated = df_all[treatment_column_name].sum()

    h = 0 # Iteration (0'th round of matching is exact matching)

    covs_match_on = all_covs
    matched_rows, return_matches, units_in_g = grouped_mr.algo2_GroupedMR(
        df_all, df_unmatched, covs_match_on, all_covs, treatment_column_name,
        outcome_column_name, return_matches)

    if (len(units_in_g)) != 0:
        bf = flame_dame_helpers.compute_bf(matched_rows, treatment_column_name, df_unmatched)

        # add the newly matched groups to MG_units, which tracks units in groups
        MG_units = MG_units + units_in_g
        # update unit weights for all units which appear in the new groups
        # flatten to 1 list, then add occurrences of unique units
        flat_units_in_g = np.concatenate(units_in_g).ravel()
        unique_units, occurrences = np.unique(flat_units_in_g, return_counts=True)
        for index in range(len(unique_units)):
            weights.loc[unique_units[index], 'weights'] += occurrences[index]
    else:
        bf = 0

		# Balancing factor of any exact matches
    return_bf.append(bf)

    # Now remove the matched units
    df_unmatched.drop(matched_rows.index, inplace=True)

    if not repeats:
        df_all = df_unmatched

    # set up all the extra dfs if needed
    if missing_holdout_replace:
        # now df_holdout is actually an array of imputed datasets
        df_holdout = flame_dame_helpers.create_mice_dfs(
            df_holdout, missing_holdout_replace, outcome_column_name)
    else:
        # df_holdout is type array regardless, just size 1 and equal to itself
        # if not doing mice.
        x = list()
        x.append(df_holdout)
        df_holdout = x

		# Predictive error of starting covariate set
    baseline_pe = flame_dame_helpers.find_pe_for_covar_set(
				df_holdout, treatment_column_name, outcome_column_name, [],
				adaptive_weights, alpha)
    return_pe.append(baseline_pe)

    # Here we initializing variables for the iterative portion of the code.
    # active_covar_sets indicates the sets elibible to be dropped. In the
    # paper, this is lambda_h. curr_covar_sets is the covariates chosen to be
    # dropped. In the paper, this is s*h. processed_covar_sets is the already
    # processed sets from previous iterations. In the paper, it's delta_h.

    active_covar_sets = set(frozenset([i]) for i in all_covs)
    processed_covar_sets = set()

    if verbose == 3:
        flame_dame_helpers.verbose_output(h, len(MG_units),
                                          df_unmatched[treatment_column_name].sum(),
                                          len(df_unmatched), orig_len_df_all,
                                          orig_tot_treated, baseline_pe,
                                          orig_len_df_all, set())

    prev_iter_num_unmatched = len(df_unmatched) # this is for output progress

    # Here, we begin the iterative dropping procedure of DAME
    while True:

        # see if any stopping criteria have been met
        if (flame_dame_helpers.stop_iterating(early_stops, df_unmatched,
                                              repeats, treatment_column_name,
                                              orig_len_df_all, h,
                                              orig_tot_treated,
                                              active_covar_sets)):
            break
        # one additional stopping criteria check:
        if (len(active_covar_sets) == 0):
            print((orig_len_df_all - len(df_unmatched)), "units matched. "\
                  "No more covariate sets to consider dropping")
            break

        # We find curr_covar_set, the best covariate set to drop.
        curr_covar_set, pe = decide_drop(
            all_covs, active_covar_sets, weight_array, adaptive_weights,
            treatment_column_name, outcome_column_name, df_holdout, alpha)

        # Check for error in above step:
        if not curr_covar_set:
            print((orig_len_df_all - len(df_unmatched)), "units matched. "\
                  "We stopped when the holdout set was not large enough or "\
                  "there was nothing left to match")
            break

        h += 1

        covs_match_on = list(set(all_covs)-curr_covar_set)

        matched_rows, return_matches, units_in_g = grouped_mr.algo2_GroupedMR(
            df_all, df_unmatched, covs_match_on, all_covs, treatment_column_name,
            outcome_column_name, return_matches)

        if (len(units_in_g)) != 0:
            # add the newly matched groups to MG_units, which tracks units in groups
            MG_units = MG_units + units_in_g
            # update unit weights for all units which appear in the new groups
            # flatten to 1 list, then add occurrences of unique units
            flat_units_in_g = np.concatenate(units_in_g).ravel()
            unique_units, occurrences = np.unique(flat_units_in_g, return_counts=True)
            for index in range(len(unique_units)):
                weights.loc[unique_units[index], 'weights'] += occurrences[index]


        # Check not equal to false because if it's turned off, value is False
        baseline_pe = max(1e-12, baseline_pe)
        if early_stops.pe and (pe - baseline_pe) / baseline_pe >= early_stops.pe:
            print("Matching stopped while attempting iteration " + str(h) +
            " due to the PE fraction early stopping criterion.")
            print("\tPredictive error of covariate set would have been " + str(pe))
            break
        return_pe.append(pe)

        # It's probably slow to compute this if people don't want it, so will
        # want to add this, I think.
        if want_bf:
            # compute balancing factor
            mg_treated = matched_rows[treatment_column_name].sum()
            mg_control = len(matched_rows) - mg_treated
            available_treated = df_unmatched[treatment_column_name].sum()
            available_control = len(df_unmatched) - available_treated
            if (available_treated != 0 and available_control != 0):
                bf = mg_treated/available_treated + mg_control/available_control
            else:
                bf = np.nan
            return_bf.append(bf)

        # Generate new active sets
        Z_h = generate_new_active_sets.algo3GenerateNewActiveSets(curr_covar_set,
                                                                  processed_covar_sets)

        # Remove curr_covar_set from the set of active sets
        active_covar_sets = active_covar_sets.difference([curr_covar_set])

        # Update the set of active sets
        active_covar_sets = active_covar_sets.union(Z_h)

        # Update the set of already processed covariate-sets. This works bc
        # processed_covar_sets is type set, but curr_covar_set is type frozenset
        processed_covar_sets.add(curr_covar_set)

        # Remove matches.
        df_unmatched = df_unmatched.drop(matched_rows.index, errors='ignore')

        if not repeats:
            df_all = df_unmatched

        # End of iter. Decide what to print to user depending on verbose var.
        if verbose == 1:
            print("Completed iteration " + str(h) + " of matching")
        if ((verbose == 2 and (h % 10 == 0)) or verbose == 3):

            flame_dame_helpers.verbose_output(h, len(MG_units),
                                              df_unmatched[treatment_column_name].sum(),
                                              len(df_unmatched),
                                              orig_len_df_all,
                                              orig_tot_treated, pe,
                                              prev_iter_num_unmatched,
                                              curr_covar_set)
            if want_bf:
                print("\tBalancing factor of this iteration: ", bf)

            prev_iter_num_unmatched = len(df_unmatched)

    # end loop.
    return_matches = return_matches.dropna(axis=0) # drop rows with nan, dont return unmatched stuff
    return_package = [return_matches]

    return_package[0] = return_package[0].join(weights)
    return_package.append(MG_units)

    # the optional returns
    if want_pe:
        return_package.append(return_pe)
    if want_bf:
        return_package.append(return_bf)

    return return_package
