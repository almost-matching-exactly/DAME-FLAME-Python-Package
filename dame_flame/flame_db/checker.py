import numpy as np
import pandas as pd

#Read in data 
def read_files(input_data, holdout_data):
    """Both options can be either df or csv files and are parsed here.
    
    Input:
        input_data: string, name of table in database
        holdout_data: The holdout data as string filename, df
        
    Return:
        holdout_data: dataframe
    """
        
    # Check the type of the input data
    if type(input_data) != str:
        raise Exception("Need to specify the name of the table that contains the dataset in your database "\
                        "frame in parameter 'input_data'")

            
    # Now read the holdout data
    if (type(holdout_data) == pd.core.frame.DataFrame):
        df_holdout = holdout_data
    elif (type(holdout_data) == str):
        df_holdout = pd.read_csv(holdout_data)
        
    else:
        raise Exception("Holdout_data shoule be a dataframe or a directory")
    
    df_holdout.columns = map(str, df_holdout.columns)
    
    return df_holdout




#Check if holdout file is legal
def check_holdout_file(df, treatment_column_name, outcome_column_name):
    '''
    This function processes the parameters passed to FLAME_db
    
    '''

    # Confirm that the treatment column name exists. 
    if (treatment_column_name not in df.columns):
        raise Exception('Invalid input error. Treatment column name does not'\
                        ' exist')
        
    # Confirm that the outcome column name exists. 
    if (outcome_column_name not in df.columns):
        raise Exception('Invalid input error. Outcome column name does not'\
                        ' exist')
        
    # column only has 0s and 1s. 
    if (set(df[treatment_column_name].unique()) != {0,1}):
        raise Exception('Invalid input error. All rows in the treatment '\
                        'column must have either a 0 or a 1 value.')
    return 


def check_stops(early_stop_un_c_frac, early_stop_un_t_frac, early_stop_pe, early_stop_pe_frac, 
                early_stop_iterations = None):
    """Check the parameters passed to DAME/FLAME relating to early stopping"""
    
    # todo: add check for epsilon on FLAME
    
    
    if ((early_stop_un_t_frac > 1.0) or (early_stop_un_t_frac < 0.0)):
        raise Exception('The value provided for the early stopping critera '\
                        'of proportion of unmatched treatment units needs to '\
                        'be between 0.0 and 1.0')
        
    if ((early_stop_un_c_frac > 1.0) or (early_stop_un_c_frac < 0.0)):
        raise Exception('The value provided for the early stopping critera '\
                        'of proportion of unmatched control units needs to '\
                        'be between 0.0 and 1.0')

    if (early_stop_pe < 0.0):
        raise Exception('The value provided for the early stopping critera '\
                        'of PE needs to be non-negative ')        
       
    if ((early_stop_pe_frac > 1.0) or (early_stop_pe_frac < 0.0)):
        raise Exception('The value provided for the early stopping critera of'\
                        ' proportion of PE needs to be between 0.0 and 1.0')
     
        
    return 

#Check all other hyperparameters:
def check_parameters(df,adaptive_weights,weight_array,C, k, ratio, matching_option,verbose,alpha, max_depth,
                     random_state, missing_data_replace, missing_holdout_replace, missing_holdout_imputations=None):   
    # Checks on the weight array...if the weight array needs to exist
    if (adaptive_weights == False):

        # Confirm that weight array has the right number of values in it
        # Subtracting 2 because one col is the treatment and one is outcome. 
        if (len(weight_array) != (len(df.columns)-2)):
            raise Exception('Invalid input error. Weight array size not equal'\
                            ' to number of columns in dataframe')

        # Confirm that weights in weight vector add to 1.
        if (abs(sum(weight_array) - 1.0) >= 0.001):
            # I do this weird operation instead of seeing if it equals one
            # to avoid floatig point addition errors that can occur. 
            raise Exception('Invalid input error. Weight array values must '\
                          'sum to 1.0')
    else:
        if (adaptive_weights != "ridge" and 
            adaptive_weights != "decisiontree"):
            raise Exception("Invalid input error. The acceptable values for "\
                            "the adaptive_weights parameter are 'ridge', "\
                            "'decisiontree'. Additionally, "\
                            "adaptive-weights may be 'False' along "\
                            "with a weight array")
    
    if(C < 0.0):
        raise Exception('The C, or the hyperparameter to trade-off between'\
                           ' balancing factor and predictive error must be '\
                           ' nonnegative. ')
    if k < 0.0 or (not isinstance(k, int)):
        raise Exception('Invalid input error. The k must be'\
            'a postive integer.')    
    if(ratio > 1.0 or ratio < 0.0):
        raise Exception('Invalid input error. ratio value must '\
                            'be positive and smaller than 1.0 \n'\
                        'Recommended 0.01 and please do not adjust it unless necessary ') 
    if (matching_option not in [0,1,2,3]):
        raise Exception('Invalid input error. matching_option value must '\
            'be 0, 1, 2 or 3') 
                        
    if (verbose not in [0,1,2,3]):
        raise Exception('Invalid input error. The verbose option must be'\
                        'the integer 0,1,2 or 3.') 
                                      
    if alpha < 0.0 or not (isinstance(alpha, int) or isinstance(alpha, float)):
        raise Exception('Invalid input error. The alpha needs to be '\
                            'positive for ridge regressions.')
    if max_depth < 0.0 or not (isinstance(max_depth, int) or isinstance(max_depth, float)):
        raise Exception('Invalid input error. The max_depth must be'\
                'a postive integer.')
    if (random_state!= None and random_state < 0.0) or not (isinstance(random_state, int) or random_state == None) :
        raise Exception('Invalid input error. The random_state  must be'\
                'a postive integer or None.')
    if  missing_data_replace not in [0,1,2]:                  
        raise Exception('Invalid input error. missing_data_replace value must '\
            'be 0, 1 or 2')                 
    if  missing_holdout_replace not in [0,1]:                  
        raise Exception('Invalid input error. missing_holdout_replace value must '\
            'be 0, or 1')                 

#     if missing_holdout_imputations <= 0.0 or (not isinstance(missing_holdout_imputations, int)):
#         raise Exception('Invalid input error. The missing_holdout_imputations must be'\
#             'a postive integer.')         
    return


#Check if input file in the database is legal
def check_input_file(df, cur, conn, treatment_column_name, outcome_column_name):
        
    db_name = df
    # Confirm that the treatment column name exists in database.
    cur.execute('''(SELECT {1} FROM {0})'''.format(db_name,treatment_column_name))
    res = np.array(cur.fetchall())

    # column only has 0s and 1s. 
    if (set(np.unique(res)) != {0,1}):
        raise Exception('Invalid input error. All rows in the treatment '\
                        'column must have either a 0 or a 1 value.')

    # Confirm that the outcome column name exists in database. 
    cur.execute('''(SELECT {1} FROM {0})'''.format(db_name,outcome_column_name))
    res = np.array(cur.fetchall())
     
    return




def check_missings(db_name, df_holdout, conn, missing_data_replace, 
                   missing_holdout_replace,treatment_column_name, outcome_column_name):
    
    cov_l = df_holdout.columns
    cur = conn.cursor()
    mice_on_holdout = False
    
    if (missing_data_replace == 0):

        cur.execute(''' select count(*) from {1} 
                        where {0}'''.format(' OR '.join([ '{1}.{0} is NULL'.format(v, db_name) for v in cov_l ]),
                                                                            db_name))
        num_null = cur.fetchall()[0][0]

        if num_null>0:
            print('There is missing data in this dataset. The default missing '\
              'data handling is being done, so we are not matching on '\
              'any missing values in the matching set')  
            missing_data_replace = 2


    if (missing_data_replace == 1):
        cur.execute(''' delete from {1} 
                        where {0}'''.format(' OR '.join([ '{1}.{0} is null'.format(v, db_name) for v in cov_l ]),
                                                                            db_name))
        conn.commit()
                        

    if (missing_data_replace == 2):
        # so replacing with large unique values will only work if columns 
        # are in order!!
        pass

    if (missing_holdout_replace == 0 and 
        df_holdout.isnull().values.any() == True):
        print('There is missing data in this dataset. The default missing '\
              'data handling is being done, so we will drop units with  missinig data')
        missing_holdout_replace = 1

    if (missing_holdout_replace == 1):
        df_holdout = df_holdout.dropna()



            
    return df_holdout
