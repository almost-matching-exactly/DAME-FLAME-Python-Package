#%% Imports
import pandas as pd
import DAME_FLAME

#%% Sample data
df = pd.read_csv("data/gen_data_sample_p5.csv")
result = DAME_FLAME.FLAME(input_data=df, verbose=0,treatment_column_name = 'treated', outcome_column_name = 'outcome')

#%% Weights test
def unit_weights_test(result_df):
    '''
    This function returns unit weights from list
    
    Parameters:
    -----------
    mmg_dict : dictionary containing all matching groups
    input_data : matching data
    '''
    
    weights = [0] * (max(result_df[0].index)+1)
    for i in range(len(result[1])):
        for j in result[1][i]:
            weights[j] += 1
    return weights

weights = unit_weights_test(result)

#%% retrieves MGs from unit indices
def MG_retrieve(return_list, groups, input_data):
    extracted = []
    for i in groups:
        indices = return_list[i]
        extracted.append(input_data.iloc[indices])
    return extracted

retrieve_test = MG_retrieve(result[1], [1,7,23,30], df)

#%% MG_index
def MG_index(return_df, input_data):
    mmg_list = []
    for i in input_data.index:
        mmg = DAME_FLAME.mmg_of_unit(return_df, i, input_data)
        if type(mmg) != bool:
            index = list(mmg.index)
            if index not in mmg_list:
                mmg_list.append(index)
    return mmg_list

test_index = MG_index(result[0],matching)

#%% MG v0.0.0
def MG_v0(return_df, input_data):
    '''
    This function returns all matched groups
    
    Parameters:
    -----------
    return_df : ouput of DAME or FLAME
    input_data : matching data
    '''
    mmg_dict = {}
    for i in input_data.index:
        mmg = DAME_FLAME.mmg_of_unit(return_df, i, input_data)
        if type(mmg) != bool:
            duplicate = []
            for j in mmg_dict:
                duplicate.append(mmg.equals(mmg_dict[j]))
            if True not in duplicate:
                mmg_dict[i] = mmg
    mmg_dict = dict(enumerate(mmg_dict[x] for x in sorted(mmg_dict)))
    return mmg_dict

test_dict = MG_v0(result[0],matching)

#%% MG v1.0.0
def MG_v1(return_df, input_data):
    '''
    This function returns all matched groups
    
    Parameters:
    -----------
    return_df : ouput of DAME or FLAME
    input_data : matching data
    '''
    k=set()
    mmg_dict = {}
    for i in input_data.index:
        mmg = DAME_FLAME.mmg_of_unit(return_df, i, input_data)
        if type(mmg) != bool:
            r=hash(mmg.values.tobytes())
            if r not in k:
                k.add(r)
                mmg_dict[i]=mmg
    mmg_dict = dict(enumerate(mmg_dict[x] for x in sorted(mmg_dict)))
    return mmg_dict

test_dict2 = MG_v1(result[0],matching)

#%% Weights
def unit_weights(mmg_dict, input_data):
    '''
    This function returns unit weights
    
    Parameters:
    -----------
    mmg_dict : dictionary containing all matching groups
    input_data : matching data
    '''
    weights = [0] * len(input_data)
    for i in mmg_dict.keys():
        for j in mmg_dict[i].index:
            weights[j] += 1
    return weights

weights = unit_weights(test_dict2, matching)

#%% CATEs
def CATE_internal(mmg_dict, return_df, input_data, treatment_column_name, 
                  outcome_column_name):
    '''
    This function returns the CATEs for all matched groups provided
    
    Parameters:
    -----------
    mmg_dict : dictionary containing matched groups
    return_df : output of DAME or FLAME
    input_data : matching data
    treatment_column_name : name of column containing treatment information
    outcome_column_name : name of column containing outcome information
    '''
    CATEs = []
    for i in mmg_dict.keys():
        df_mmg = mmg_dict[i]
        treated = df_mmg.loc[df_mmg[treatment_column_name] == 1]
        control = df_mmg.loc[df_mmg[treatment_column_name] == 0]
        avg_treated = sum(treated[outcome_column_name])/len(treated.index)
        avg_control = sum(control[outcome_column_name])/len(control.index)
        CATEs.append(avg_treated - avg_control)
    return CATEs
        
CATEs = CATE_internal(test_dict,result[0],matching,'treated','outcome')

#%% ATE v0.0.0
def ATE_v0(return_df, input_data, treatment_column_name, outcome_column_name):
    '''
    This function returns the ATE for post-matching analysis using te_of_unit
    
    Parameters:
    -----------
    return_df : output of DAME or FLAME
    input_data : matching data
    treatment_column_name : name of column containing treatment information
    outcome_column_name : name of column containing outcome information
    '''
    te_list = []
    for i in input_data.index:
        #estimate treatment effect for each unit
        te = DAME_FLAME.te_of_unit(return_df, i, input_data, 
                                              treatment_column_name, 
                                              outcome_column_name)
        te_list.append(te)
    return sum(te_list) / len(te_list)

print(ATE_v0(result[0],matching,'treated','outcome'))

#%% ATE v1.0.0
def ATE_v1(mmg_dict, weights, CATEs, return_df, input_data, 
           treatment_column_name, outcome_column_name):
    '''
    This function returns the ATE for post-matching analysis using unit weights
    
    Parameters:
    -----------
    mmg_dict : dictionary containing all matched groups
    weights : list of unit weights
    CATEs : list of CATEs for every matched group
    return_df : output of DAME or FLAME
    input_data : matching data
    treatment_column_name : name of column containing treatment information
    outcome_column_name : name of column containing outcome information
    '''
    weight_sum = 0; weighted_CATE_sum = 0
    for i in mmg_dict.keys():
        df_mmg = mmg_dict[i]
        MG_weight = 0;
        for j in df_mmg.index:
            MG_weight += weights[j]
        weight_sum += MG_weight
        weighted_CATE_sum += MG_weight * CATEs[i]
    return weighted_CATE_sum / weight_sum

print(ATE_v1(test_dict, weights, CATEs, result[0], matching, 'treated','outcome'))

#%% ATT v0.0.0
def ATT_v0(return_df, input_data, treatment_column_name, outcome_column_name, 
        weights):
    '''
    This function returns the ATT for post-matching analysis using 
    imputation estimation
    
    Parameters:
    -----------
    return_df : output of DAME or FLAME
    input_data : matching data
    treatment_column_name : name of column containing treatment information
    outcome_column_name : name of column containing outcome information
    '''
    te_list = []
    for i in input_data.index:
        #we need to isolate treated units
        if input_data[treatment_column_name][i] == 1:
            #now we access the mmg for each treated unit
            df_mmg = DAME_FLAME.mmg_of_unit(return_df, i,
                                            input_data)
            if type(df_mmg) != bool:
                control = df_mmg.loc[df_mmg[treatment_column_name] == 0]
                #we then predict the counterfactual outcome
                control_avg = sum(control[outcome_column_name])/len(control.index)
                #finally we estimate treatment effect
                te = input_data[outcome_column_name][i] - control_avg
                #we weight treatment effects using control unit weights
                MG_weight = 0
                for j in control.index:
                    MG_weight += weights[j]
                te_list.append(MG_weight * te)
    return sum(te_list) / len(te_list)

print(ATT_v0(result[0],matching,'treated','outcome',weights))

#%% ATT v1.0.0
def ATT_v1(return_df, input_data, treatment_column_name, outcome_column_name, 
        weights):
    '''
    This function returns the ATT for post-matching analysis using
    balancing estimation
    
    Parameters:
    -----------
    return_df : output of DAME or FLAME
    input_data : matching data
    treatment_column_name : name of column containing treatment information
    outcome_column_name : name of column containing outcome information
    '''
    treated = input_data.loc[input_data[treatment_column_name] == 1]
    control = input_data.loc[input_data[treatment_column_name] == 0]
    control_weights = [weights[i] for i in list(control.index)]
    avg_treated = sum(treated[outcome_column_name])/len(treated.index)
    control_weight_sum = sum(control_weights)
    avg_control = sum(control[outcome_column_name] * control_weights)/control_weight_sum
    return avg_treated - avg_control

print(ATT_v1(result[0],matching,'treated','outcome',weights))
