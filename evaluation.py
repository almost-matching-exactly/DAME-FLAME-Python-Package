# -*- coding: utf-8 -*-
"""
Neha
This is disgustingly inefficient, but since I'm changing the output style,
it doesn't really make sense to be cleaner right now
"""

def calc_ate(return_covs_list, return_matched_group, 
                            return_matched_data, df, 
                            treatment_column_name, 
                            outcome_column_name):
    '''
    This function calculates the ATE
    So on each iteration, there are a certain number of matched groups. 
    The CATE for each of these matched groups is the average treated outcome 
    minus the average untreated outcome. Then, the ATE is computed by:
    ‘Concatenate’ across all iterations and treat them equally 
    (as if all the matching somehow happened in one iteration) and then perform
    a weighted average (again, across all iterations) of the CATEs by the MG sizes.
    
    Input: return_matched_data: List of tuples (unit num, group num). indicates 
            what unit numbers belong to what group numbers.
    '''
    group_ato = dict() # average treated outcome of each group
    group_auo = dict() # average untreated outcome of each group
    group_num_treated = dict() # number of treated in each group
    group_num_untreated = dict() # number of untreated in each group
    
    # in this loop, we just sum up all of the treated outcome/untreated outcomes
    # and add to the number of treated/untreated
    for item in return_matched_data:
        row_number, group_number = item
        # each item is a tuple (row number, group number)
        treated = df[treatment_column_name][row_number]
        if treated == 0:
            if group_number in group_num_untreated:
                group_num_untreated[group_number] += 1
                group_auo[group_number] += df[outcome_column_name][row_number]
            else:
                group_num_untreated[group_number] = 1
                group_auo[group_number] = df[outcome_column_name][row_number]
        else:
            if group_number in group_num_treated:
                group_num_treated[group_number] += 1
                group_ato[group_number] += df[outcome_column_name][row_number]
            else:
                group_num_treated[group_number] = 1
                group_auo[group_number] = df[outcome_column_name][row_number]
                
    
    # now we get the averages, or compute cates. 
    group_cate = dict()
    for key, value in group_ato.items():
        group_cate[key] = group_ato[key]/group_num_treated[key] - group_auo[key]/group_num_untreated[key]

    # now lastly, we compute the ate.
    ate = 0
    number_units = len(df)
    for key, value in group_cate.items():
        # += CATE of group*(number of treated in group + number of untreated)/total num units
        ate += group_cate[key]*(group_num_untreated[key] + group_num_treated[key])/number_units
        
    return ate