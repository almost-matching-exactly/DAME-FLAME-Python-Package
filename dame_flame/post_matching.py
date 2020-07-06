#%% Imports
import pandas as pd
import numpy as np
import dame_flame
import time
from . import DAME_FLAME

#%% Original algorithm speed test
df = pd.read_csv("data/data.csv")

start_original = time.time()
result = dame_flame.DAME_FLAME.FLAME(input_data=df, holdout_data = df,verbose=0,treatment_column_name = 'treated', outcome_column_name = 'outcome',repeats = True)
end_original = time.time()
print(end_original - start_original)

#%% Modified algorithm speed test
df = pd.read_csv("data/data.csv")

start_new = time.time()
result_new = DAME_FLAME.FLAME(input_data=df, holdout_data = df,verbose=0,treatment_column_name = 'treated', outcome_column_name = 'outcome',repeats = True)
end_new = time.time()
print(end_new - start_new)

#%% MG function
def MG(return_df, unit_ids, input_data):
    '''
    This function returns the main matched groups for all specified unit
    indices

    Args:
        return_df : output of DAME or FLAME
        unit_id : units for which CATE will be computed
        input_data : matching data
        treatment_column_name : name of column containing treatment information
        outcome_column_name : name of column containing outcome information
    '''
    #accept int or list
    if type(unit_ids) is int:
        unit_ids = [unit_ids]
    #define relevant output variables
    MGs = return_df[1]
    #recover MMG
    MMGs = []
    for i in unit_ids:
        status = 0
        for j in MGs:
            if i in j:
                MMGs.append(input_data.loc[j])
                status = 1
                break
        #warn user that unit has no matches
        if status == 0:
            MMGs.append(np.nan)
            print('Unit ' + str(i) + ' does not have any matches')
    #format output
    if len(MMGs) == 1:
        MMGs = MMGs[0]
    return MMGs
       
print(MG(result_new, 0, df))

#%% CATEs function
def CATE(return_df, unit_ids, input_data, treatment_column_name = 'treated', 
         outcome_column_name = 'outcome'):
    '''
    This function returns the CATEs for all specified unit indices
    
    Args:
        return_df : output of DAME or FLAME
        unit_id : units for which CATE will be computed
        input_data : matching data
        treatment_column_name : name of column containing treatment information
        outcome_column_name : name of column containing outcome information
    '''
    #accept int or list
    if type(unit_ids) is int:
        unit_ids = [unit_ids]
    #define relevant output variables
    MGs = return_df[1]
    #recover CATEs
    CATEs = []
    for i in unit_ids:
        status = 0
        for j in MGs:
            if i in j:
                df_mmg = input_data.loc[j,[treatment_column_name, 
                                                outcome_column_name]]
                status = 1
                break
        if status == 0:
            CATEs.append(np.nan)
            print('Unit ' + str(i) + " does not have any matches, so can't " \
                  "find the CATE")
        else:
            treated = df_mmg.loc[df_mmg[treatment_column_name] == 1]
            control = df_mmg.loc[df_mmg[treatment_column_name] == 0]
            avg_treated = sum(treated[outcome_column_name])/len(treated.index)
            avg_control = sum(control[outcome_column_name])/len(control.index)
            CATEs.append(avg_treated - avg_control)
    #format output
    if len(CATEs) == 1:
        CATEs = CATEs[0]
    return CATEs
        
print(CATE(result_new, 0, df))

#%% ATE function
def ATE(return_df, input_data, treatment_column_name = 'treated',
         outcome_column_name = 'outcome'):
    '''
    This function returns the ATE for the matching data
    
    Args:
        return_df : output of a call to DAME or FLAME
        input_data : matching data
        treatment_column_name : name of column containing treatment information
        outcome_column_name : name of column containing outcome information
    '''
    #define relevant output variables
    MGs = return_df[1]
    weights = return_df[0]['weights']
    #recover CATEs
    CATEs = [0] * len(MGs)
    for i in range(len(MGs)):
        group_data = input_data.loc[MGs[i], [treatment_column_name, outcome_column_name]]
        treated = group_data.loc[group_data[treatment_column_name] == 1]
        control = group_data.loc[group_data[treatment_column_name] == 0]
        avg_treated = sum(treated[outcome_column_name]) / len(treated.index)
        avg_control = sum(control[outcome_column_name]) / len(control.index)
        CATEs[i] = avg_treated - avg_control
    #compute ATE
    weight_sum = 0; weighted_CATE_sum = 0
    for i in range(len(MGs)):
        MG_weight = 0;
        for j in MGs[i]:
            MG_weight += weights[j]
        weight_sum += MG_weight
        weighted_CATE_sum += MG_weight * CATEs[i]
    return weighted_CATE_sum / weight_sum

print(ATE(result_new, df))

#%% ATT function
def ATT(return_df, input_data, treatment_column_name = 'treated',
        outcome_column_name = 'outcome'):
    '''
    This function returns the ATT for the matching data using
    balancing estimation
    
    Args:
        return_df : output of DAME or FLAME
        input_data : matching data
        treatment_column_name : name of column containing treatment information
        outcome_column_name : name of column containing outcome information
    '''
    #define relevant output variables
    weights = return_df[0]['weights']
    treated = input_data.loc[input_data[treatment_column_name] == 1]
    control = input_data.loc[input_data[treatment_column_name] == 0]
    #compute ATT
    avg_treated = sum(treated[outcome_column_name])/len(treated.index)
    control_weights = weights[control.index]
    control_weight_sum = sum(control_weights)
    avg_control = sum(control[outcome_column_name] * control_weights)/control_weight_sum
    return avg_treated - avg_control

print(ATT(result_new, df))
