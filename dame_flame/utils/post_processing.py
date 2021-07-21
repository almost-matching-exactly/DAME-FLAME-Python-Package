# -*- coding: utf-8 -*-
""" Find Treatment Effect Estimators, and Matched Groups, of matched units.
"""

# author: Neha Gupta, Tommy Howell, Duke University
# Copyright Duke University 2020
# License: MIT

import numpy as np
from .. import matching

def validate_matching_obj(matching_object):
    """ Check matching_object's type and that .fit(), .predict() done"""

    if matching.MatchParent not in type(matching_object).__bases__:
        raise Exception("The matching_object input parameter needs to be "\
                        "of type DAME or FLAME")
    if (not hasattr(matching_object, 'input_data')):
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

    validate_matching_obj(matching_object)

    if (matching_object.missing_data_replace != 3):
        array_mgs = matching_object.units_per_group
        df_matched_units = matching_object.df_units_and_covars_matched
    else:
        array_mgs = matching_object.units_per_group[mice_iter]
        df_matched_units = matching_object.df_units_and_covars_matched[mice_iter]


    main_matched_groups = []

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
                    main_matched_groups.append(new_group)
                    break
        # Warn user if a unit has no matches
        else:
            main_matched_groups.append(np.nan)
            print('Unit ' + str(unit) + ' does not have any matches')
    # Format output
    if len(main_matched_groups) == 1:
        main_matched_groups = main_matched_groups[0]
    return main_matched_groups


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

    validate_matching_obj(matching_object)


    if (matching_object.missing_data_replace != 3):
        arr_matched_groups = matching_object.units_per_group        
        df_matched_units = matching_object.df_units_and_covars_matched
    else:
        arr_matched_groups = matching_object.units_per_group[mice_iter]
        df_matched_units = matching_object.df_units_and_covars_matched[mice_iter]

    # Recover CATEs
    cates = []
    for unit in unit_ids:
        if unit in df_matched_units.index:
            for group in arr_matched_groups:
                # The first group to contain the specified unit is the MMG
                if unit in group:
                    df_mmg = matching_object.input_data.loc[group, 
                        [matching_object.treatment_column_name,
                         matching_object.outcome_column_name]]
                    break
            # Assuming an MMG has been found, compute CATE for that group
            treated = df_mmg.loc[df_mmg[matching_object.treatment_column_name] == 1]
            control = df_mmg.loc[df_mmg[matching_object.treatment_column_name] == 0]
            avg_treated = sum(treated[matching_object.outcome_column_name])/len(treated.index)
            avg_control = sum(control[matching_object.outcome_column_name])/len(control.index)
            cates.append(avg_treated - avg_control)
        # Warn user that unit has no matches
        else:
            cates.append(np.nan)
            if matching_object.verbose != 0:
                print('Unit ' + str(unit) + " does not have any matches, so " \
                      "can't find the CATE")

    # Format output
    if len(cates) == 1:
        cates = cates[0]
    return cates

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
        arr_matched_groups = matching_object.units_per_group
        num_groups_per_unit = matching_object.groups_per_unit
    else:
        arr_matched_groups = matching_object.units_per_group[mice_iter]
        num_groups_per_unit = matching_object.groups_per_unit[mice_iter]

    # Recover CATEs
    cates = [0] * len(arr_matched_groups) # this will be a CATE for each matched group
    for group_id in range(len(arr_matched_groups)):
        group_data = matching_object.input_data.loc[arr_matched_groups[group_id],
                                                    [matching_object.treatment_column_name,
                                                     matching_object.outcome_column_name]]
        treated = group_data.loc[group_data[matching_object.treatment_column_name] == 1]
        control = group_data.loc[group_data[matching_object.treatment_column_name] == 0]
        try:
            avg_treated = sum(treated[matching_object.outcome_column_name]) / len(treated.index)
            avg_control = sum(control[matching_object.outcome_column_name]) / len(control.index)
        except:
            print("There was an error in the matching process.", group_id)
            break
        cates[group_id] = avg_treated - avg_control

    # Compute ATE
    weight_sum = 0
    weighted_cate_sum = 0
    for group_id in range(len(arr_matched_groups)):
        matched_group_weight = 0
        for unit in arr_matched_groups[group_id]:
            matched_group_weight += num_groups_per_unit[unit]
        weight_sum += matched_group_weight
        weighted_cate_sum += matched_group_weight * cates[group_id]

    return weighted_cate_sum/weight_sum



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
        matched_df = matching_object.input_data.loc[
            matching_object.df_units_and_covars_matched.index]
    else:
        num_groups_per_unit = matching_object.groups_per_unit[mice_iter]
        matched_df = matching_object.input_data.loc[
            matching_object.df_units_and_covars_matched[mice_iter].index]

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
