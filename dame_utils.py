import pandas as pd
import query_mmg


def mmg_of_unit(return_df, unit_id, input_data, output_style=1):
    """
    This function allows a user to find the main matched group of a particular
    unit, after the main DAME algorithm has already been run and all matches
    have been found. 
    
    Args:
        return_df: The return value from DAME above
        unit_id(int): the unit aiming to find the mmg of
        file_name: The csv file containing all of the original data.
        output_style: 1 if you want just the covariates matched on, and 2 if
        you want all of the attributes listed. 
    """
    if type(input_data) == pd.core.frame.DataFrame:
        df = input_data
    else:
        df = pd.read_csv(return_df)
        
    mmg_df = query_mmg.find(return_df, unit_id, df)
    if output_style == 2:
        return input_data.loc[mmg_df.index]
    else:
        # so now we need to filter on just the ones we want. 
        if ("*" in return_df.loc[unit_id].unique()):
            # this means there is a star and it needs to be filtered. 
            my_series = return_df.loc[unit_id]
            star_cols = my_series[my_series == "*"].index
            non_star_cols = input_data.columns.difference(star_cols)
            return input_data[non_star_cols].loc[mmg_df.index]
        

def te_of_unit(return_df, unit_id, input_data, treatment_column_name, outcome_column_name):
    """
    This function allows a user to find the main matched group of a particular
    unit, after the main DAME algorithm has already been run and all matches
    have been found. 
    
    Args:
        return_df: The return value from DAME above
        unit_id: the unit aiming to find the mmg of. Type int.
        file_name: The csv file containing all of the original data.
    """
    df_mmg = mmg_of_unit(return_df, unit_id, input_data)
    
    if type(input_data) == pd.core.frame.DataFrame:
        df = input_data
    else:
        df = pd.read_csv(return_df)
        
    return query_ate.find(df_mmg, unit_id, df, treatment_column_name, outcome_column_name)

##### These are fancy versions of the above functions for pretty prints, etc ######

def mmg_and_te_of_unit(return_df, unit_id, input_data, treatment_column_name, outcome_column_name):
    """
    Fancy version of above function.
    """
    df_mmg = mmg_of_unit(return_df, unit_id, input_data)
    
    if type(input_data) == pd.core.frame.DataFrame:
        df = input_data
    else:
        df = pd.read_csv(return_df)
        
    return df_mmg, query_ate.find(df_mmg, unit_id, df, treatment_column_name, outcome_column_name)

def print_te_and_mmg(return_df, unit_id, input_data, treatment_column_name, outcome_column_name):
    """
    Fancy version of above function.
    """
    df_mmg = mmg_of_unit(return_df, unit_id, input_data)
    
    if type(input_data) == pd.core.frame.DataFrame:
        df = input_data
    else:
        df = pd.read_csv(return_df)
        
    print("This is the Main Matched Group of unit", unit_id, ":")
    print(df_mmg)
    print("This is the treatment effect of unit", unit_id, ":")
    print(unit_id)