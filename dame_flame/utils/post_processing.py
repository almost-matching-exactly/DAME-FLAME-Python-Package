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
            
def all_MGs(matching_object):
    '''
    This function returns all of the main matched groups, for every unit.
    It's slow! Use function "MG" instead if you want the matched group for
    only specific units.
    '''
    validate_matching_obj(matching_object)
    
    mgs_dict = dict()
    
    for group in matching_object.units_per_group:
        for index in group:
            if index not in mgs_dict:
                mgs_dict[index] = group
                
    return mgs_dict


def MG(matching_object, unit_ids, output_style=1, mice_iter=0):
    '''
    This function returns the main matched groups for all specified unit
    indices

    Args:
        matching_object (DAME or FLAME object)
        unit_ids (int, list): units for which MG will be returned

    Returns:
        MMGs: list of dataframes or singular dataframe containing the units
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
                            new_group[col] = ["*"] * len(new_group.index)
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

def var_ATE(matching_object):
    '''
    This is an EXPERIMENTAL function that implements the variance found in 
    Abadie, Drukker, Herr, and Imbens (The Stata Journal, 2004) assuming
    constant treatment effect and homoscedasticity. Note that the implemented 
    estimator is NOT asymptotically normal and so in particular, 
    asymptotically valid confidence intervals or hypothesis tests cannot be 
    conducted on its basis. In the future, the estimation procedure will be 
    changed.

    Returns
    -------
    variance: float
    ATE: float
    '''
    validate_matching_obj(matching_object)

    # Compute the sigma^2 estimate from equation 10 in Abadie et al
    # units_per_group is in format [[#,#,#,...], [#,#,#,...],..]
    units_per_group = matching_object.units_per_group
    
    mmgs_dict = all_MGs(matching_object)
        
    # Compute K_dict, which maps i to KM value
    K_dict = dict.fromkeys(mmgs_dict,0)
    km_temp = 0
    treated_col = matching_object.treatment_column_name
    for i in matching_object.df_units_and_covars_matched.index:        
        # iterate through all matched units of indexes with opposite treatment
        # values. How many of those MMGs am I in, and
        # if I'm in someone's MMG, what is the size of their MMG?

        is_treatment_val = matching_object.input_data.loc[i, treated_col]
        
        ''' # Possible speed improvement to explore -- only works for without repeats
        for group in units_per_group:
            if i in group:
                # find out how many people in this mmg
                # have the opposite treatment status to the treatment_val_mmg
                num_treated = sum(matching_object.input_data.loc[group, 'treated'])
                if is_treatment_val:
                    num_opposite = len(group) - num_treated
                else:
                    num_opposite = num_treated
                    
                K_dict[i] += num_opposite/(len(group)-num_opposite)
        ''' 
        # This works for both with and without repeats. Technically somewhat slower though!
        for j in matching_object.df_units_and_covars_matched.index:
            if i in mmgs_dict[j] and matching_object.input_data.loc[j, treated_col] != is_treatment_val:
                num_treated = sum(matching_object.input_data.loc[mmgs_dict[j], treated_col])
                if matching_object.input_data.loc[j, treated_col]: # you have to be opposite of j != opp of i
                    num_opposite = len(mmgs_dict[j]) - num_treated
                else:
                    num_opposite = num_treated
                K_dict[i] += 1/num_opposite
        
    # Compute ATE per simple estimator in paper -- this should be right
    ate = 0
    for i in mmgs_dict:
        treatment_val = matching_object.input_data.loc[i, treated_col]
        outcome_val = matching_object.input_data.loc[
            i, matching_object.outcome_column_name]
        ate += ((2*treatment_val - 1)*(1 + K_dict[i])*outcome_val)
    ate = ate/len(mmgs_dict)
        
    # Compute sigma^2. 
    i_summation = 0
    for i in mmgs_dict:
        group_members = mmgs_dict[i] # these are the l values in Jm(i)
        treatment_val = matching_object.input_data.loc[i, treated_col]
        outcome_val = matching_object.input_data.loc[
            i, matching_object.outcome_column_name]
        opp_group_members = matching_object.input_data.loc[group_members].index[matching_object.input_data.loc[group_members][treated_col] != treatment_val].tolist()
        # iterate through my group members -- only the ones w opp treatment to me!
        temp_l_summation = 0
        for l in opp_group_members:
            Y_l = matching_object.input_data.loc[
            l, matching_object.outcome_column_name]
            if treatment_val:
                temp_l_summation += ((outcome_val - Y_l - ate)**2)
            else:
                temp_l_summation += ((Y_l - outcome_val - ate)**2)         
        i_summation += temp_l_summation/len(opp_group_members)
    sigma_squared = 1/(2*len(mmgs_dict))*i_summation
    
    # Combine the above to compute var_estimator
    dict_summation = 0
    for key, value in K_dict.items():
        dict_summation += (1+value)**2
    var_estimator = sigma_squared*dict_summation/(len(mmgs_dict)**2)
    
    return var_estimator, ate