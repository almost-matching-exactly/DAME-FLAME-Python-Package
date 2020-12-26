# -*- coding: utf-8 -*-
""" Find Treatment Effect Estimators, and Matched Groups, of matched units.
"""

# author: Neha Gupta, Tommy Howell, Duke University
# Copyright Duke University 2020
# License: MIT

import pandas as pd
import numpy as np
from .. import matching

def validate_matching_obj(matching_object):
    """ Check matching_object's type and that .fit(), .predict() done"""

    if matching.MatchParent not in type(matching_object).__bases__:
        raise Exception("The matching_object input parameter needs to be "\
                        "of type DAME or FLAME")
    if (hasattr(matching_object, 'input_data') == False):
        raise Exception("This function can be only called after a match has "\
                       "been formed using the .fit() and .predict() functions")

def MG(matching_object, unit_ids, output_style=1, mice_iter=0):
    '''
    This function returns the main matched groups for all specified unit
    indices

    Args:
        matching_object (DAME or FLAME object)
        unit_ids (int, list): units for which MG will be returned

    Returns:
        MMGs: list of datraframes or singular dataframe containing the units
            in the main matched groups for the specified units

    '''
    # Accept int or list for unit_id
    if type(unit_ids) is int:
        unit_ids = [unit_ids]
    # todo: error check this. If it's not an int or an iteratable object of ints,
    # or if the unit ids dont exist, need to throw an error.

    validate_matching_obj(matching_object)

    if (matching_object.missing_data_replace != 3):
        array_mgs = matching_object.units_per_group
        df_matched_units = matching_object.df_units_and_covars_matched
    else:
        array_mgs = matching_object.units_per_group[mice_iter]
        df_matched_units = matching_object.df_units_and_covars_matched[mice_iter]


    MMGs = []

    # Now we recover MMG
    for unit in unit_ids:
        if unit in df_matched_units.index:
            # Iterate through all matched groups
            for group in array_mgs:
                # The first group to contain the specified unit is the MMG
                if unit in group:
                    new_group = matching_object.input_data.loc[group]
                    my_series = df_matched_units.loc[unit]
                    if output_style == 1 and "*" in my_series.unique():
                        # Insert asterisks for unused covariates
                        star_cols = my_series[my_series == "*"].index
                        for col in star_cols:
                            new_group[[col]] = ['*'] * len(new_group.index)
                    MMGs.append(new_group)
                    break
        # Warn user if a unit has no matches
        else:
            MMGs.append(np.nan)
            print('Unit ' + str(unit) + ' does not have any matches')
    # Format output
    if len(MMGs) == 1:
        MMGs = MMGs[0]
    return MMGs


def CATE(matching_object, unit_ids, mice_iter=0):
    '''
    This function returns the CATEs for all specified unit indices

    Args:
        matching_object (DAME or FLAME object)
        unit_ids (int, list): units for which MG will be returned

    Returns:
        CATEs: list of floats or singular float containing the CATEs
            of the main matched groups for the specified units

    '''

    # Accept int or list for unit_id
    if type(unit_ids) is int:
        unit_ids = [unit_ids]
    # todo: error trap this. If it's not an int or an iteratable object of ints,
    # or if the unit ids dont exist, need to throw an error.

    validate_matching_obj(matching_object)


    if (matching_object.missing_data_replace != 3):
        array_MGs = matching_object.units_per_groups        
        df_matched_units = matching_object.df_units_and_covars_matched
    else:
        array_MGs = matching_object.units_per_group[mice_iter]
        df_matched_units = matching_object.df_units_and_covars_matched[mice_iter]

    # Recover CATEs
    CATEs = []
    for unit in unit_ids:
        if unit in df_matched_units.index:
            for group in array_MGs:
                # The first group to contain the specified unit is the MMG
                if unit in group:
                    df_mmg = matching_object.input_data.loc[group, [matching_object.treatment_column_name,
                                                                    matching_object.outcome_column_name]]
                    break
            # Assuming an MMG has been found, compute CATE for that group
            treated = df_mmg.loc[df_mmg[matching_object.treatment_column_name] == 1]
            control = df_mmg.loc[df_mmg[matching_object.treatment_column_name] == 0]
            avg_treated = sum(treated[matching_object.outcome_column_name])/len(treated.index)
            avg_control = sum(control[matching_object.outcome_column_name])/len(control.index)
            CATEs.append(avg_treated - avg_control)
        # Warn user that unit has no matches
        else:
            CATEs.append(np.nan)
            if matching_object.verbose != 0:
                print('Unit ' + str(unit) + " does not have any matches, so " \
                      "can't find the CATE")

    # Format output
    if len(CATEs) == 1:
        CATEs = CATEs[0]
    return CATEs

def ATE(matching_object, mice_iter=0):
    '''
    This function returns the ATE for the matching data

    Args:
        matching_object (DAME or FLAME object)
    Returns:
        ATE: the average treatment effect for the matching data

    '''

    validate_matching_obj(matching_object)

    if matching_object.missing_data_replace != 3:
        array_MGs = matching_object.units_per_group
        num_groups_per_unit = matching_object.groups_per_unit
    else:
        array_MGs = matching_object.units_per_group[mice_iter]
        num_groups_per_unit = matching_object.groups_per_unit[mice_iter]

    # Recover CATEs
    CATEs = [0] * len(array_MGs) # this will be a CATE for each matched group
    for group_id in range(len(array_MGs)):
        group_data = matching_object.input_data.loc[array_MGs[group_id],
                                                    [matching_object.treatment_column_name,
                                                     matching_object.outcome_column_name]]
        treated = group_data.loc[group_data[matching_object.treatment_column_name] == 1]
        control = group_data.loc[group_data[matching_object.treatment_column_name] == 0]
        avg_treated = sum(treated[matching_object.outcome_column_name]) / len(treated.index)
        avg_control = sum(control[matching_object.outcome_column_name]) / len(control.index)
        CATEs[group_id] = avg_treated - avg_control
    # Compute ATE
    weight_sum = 0
    weighted_CATE_sum = 0
    for group_id in range(len(array_MGs)):
        MG_weight = 0
        for unit in array_MGs[group_id]:
            MG_weight += num_groups_per_unit[unit]
        weight_sum += MG_weight
        weighted_CATE_sum += MG_weight * CATEs[group_id]
    ATE = weighted_CATE_sum / weight_sum
    return ATE



def ATT(matching_object, mice_iter=0):
    '''
    This function returns the ATT for the matching data using
    balancing estimation

    Args:
        matching_object (DAME or FLAME object)
    Returns:
        ATT: the average treatment effect on the treated for the matching data
    '''

    validate_matching_obj(matching_object)

    if matching_object.missing_data_replace != 3:
        num_groups_per_unit = matching_object.groups_per_unit
        matched_df = matching_object.input_data.loc[matching_object.df_units_and_covars_matched.index]
    else:
        num_groups_per_unit = matching_object.groups_per_unit[mice_iter]
        matched_df = matching_object.input_data.loc[matching_object.df_units_and_covars_matched[mice_iter].index]

    treated = matched_df.loc[matched_df[matching_object.treatment_column_name] == 1]
    control = matched_df.loc[matched_df[matching_object.treatment_column_name] == 0]
    # Compute ATT
    avg_treated = sum(treated[matching_object.outcome_column_name])/len(treated.index)
    # Stores weights for all control units
    control_weights = []
    for unit in control.index:
        if unit in num_groups_per_unit.index:
            control_weights.append(num_groups_per_unit[unit])
        else:
            # Unmatched units have a weight of 0
            control_weights.append(0)
    control_weight_sum = sum(control_weights)
    avg_control = sum(control[matching_object.outcome_column_name] * control_weights)/control_weight_sum
    return avg_treated - avg_control
