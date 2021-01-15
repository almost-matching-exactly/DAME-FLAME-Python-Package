import numpy as np
import pandas as pd
from flame_db.gen_insert_data import *
from flame_db.FLAME_db_algorithm import *
from flame_db.matching_helpers import *
from flame_db.utils import *
import unittest
import pandas as pd
import os
import sys




def check_statistics(res_post_new):
    ATE_ = ATE_db(res_post_new)
    ATT_ = ATT_db(res_post_new)
    if type(ATE_) == np.nan:
        print("ATE: " + str(ATE_))
        return True
    if type(ATT_) == np.nan:
        print("ATT:" + str(ATT_))
        return True
    return False


p = 20
TE = 5
gen_data_db(n = 1000,p = 2, TE = TE)
data,weight_array = gen_data_db(n = 1000,p = p, TE = TE)
holdout,weight_array = gen_data_db(n = 500,p = p, TE = TE)

#Connect to the database
select_db = "postgreSQL"  # Select the database you are using
database_name='tmp' # database name
host = 'localhost' #host ='vcm-17819.vm.duke.edu' # "127.0.0.1"
port = "5432"
user="postgres"
password= ""
conn = connect_db(database_name, user, password, host, port)


class Test_exceptions(unittest.TestCase):
    
    def test_false_weights_type(self):
        def broken_weights_type():
            res_post_new2 = FLAME_db(input_data = "test_df", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    C = 0.1,
                                    conn = conn,
                                    matching_option = 2,
                                    adaptive_weights = 'safdsaf',
                                    verbose = 3,
                                    k = 0
                                    )
        with self.assertRaises(Exception) as _weights_type:
            broken_weights_type()
            
        self.assertTrue("Invalid input error. The acceptable values for "\
                            "the adaptive_weights parameter are 'ridge', "\
                            "'decisiontree'. Additionally, "\
                            "adaptive-weights may be 'False' along "\
                            "with a weight array" in str(_weights_type.exception))

    def test_false_weight_array_len(self):
        def broken_weight_array_len():
            res_post_new2 = FLAME_db(input_data = "test_df", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    C = 0.1,
                                    conn = conn,
                                    adaptive_weights = False,
                                    matching_option = 2,
                                    weight_array = [1],
                                    verbose = 3,
                                    k = 0
                                    )
        with self.assertRaises(Exception) as weight_array_len:
            broken_weight_array_len()
            
        self.assertTrue('Invalid input error. Weight array size not equal'\
                            ' to number of columns in dataframe' in str(weight_array_len.exception))
        
        
    def test_false_weight_array_sum(self):
        def broken_weight_array_sum():
            res_post_new2 = FLAME_db(input_data = "test_df", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    C = 0.1,
                                    conn = conn,
                                    adaptive_weights = False,
                                    matching_option = 2,
                                    weight_array = [1]*p,
                                    verbose = 3,
                                    k = 0
                                    )
        with self.assertRaises(Exception) as weight_array_sum:
            broken_weight_array_sum()
            
        self.assertTrue('Invalid input error. Weight array values must '\
                            'sum to 1.0' in str(weight_array_sum.exception))
        
        
    def test_false_alpha(self):
        def broken_alpha():
            res_post_new2 = FLAME_db(input_data = "test_df", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    C = 0.1,
                                    conn = conn,
                                    alpha = -10,
                                    verbose = 3,
                                    k = 0
                                    )
        with self.assertRaises(Exception) as alpha:
            broken_alpha()
            
        self.assertTrue('Invalid input error. The alpha needs to be '\
                            'positive for ridge regressions.' in str(alpha.exception))
        
        
    def test_false_C(self):
        def broken_C():
            res_post_new2 = FLAME_db(input_data = "test_df", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    C = -10,
                                    conn = conn,
                                    verbose = 3,
                                    k = 0
                                    )
        with self.assertRaises(Exception) as C:
            broken_C()
            
        self.assertTrue('The C, or the hyperparameter to trade-off between'\
                           ' balancing factor and predictive error must be '\
                           ' nonnegative. 'in str(C.exception))

    def test_false_k(self):
        def broken_k():
            res_post_new2 = FLAME_db(input_data = "test_df", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    conn = conn,
                                    verbose = 3,
                                    k = -10
                                    )
        with self.assertRaises(Exception) as k:
            broken_k()
            
        self.assertTrue('Invalid input error. The k must be'\
            'a postive integer.'in str(k.exception))

        
    def test_false_ratio(self):
        def broken_ratio():
            res_post_new2 = FLAME_db(input_data = "test_df", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    conn = conn,
                                    verbose = 3,
                                    ratio = -10
                                    )
        with self.assertRaises(Exception) as ratio:
            broken_ratio()
            
        self.assertTrue('Invalid input error. ratio value must '\
                            'be positive and smaller than 1.0 \n'\
                        'Recommended 0.01 and please do not adjust it unless necessary 'in str(ratio.exception))
        
        
    def test_false_matching_option(self):
        def broken_matching_option():
            res_post_new2 = FLAME_db(input_data = "test_df", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    conn = conn,
                                    verbose = 3,
                                    matching_option = -10
                                    )
        with self.assertRaises(Exception) as matching_option:
            broken_matching_option()
            
        self.assertTrue('Invalid input error. matching_option value must '\
            'be 0, 1, 2 or 3'in str(matching_option.exception))
        
    def test_false_verbose(self):
        def broken_verbose():
            res_post_new2 = FLAME_db(input_data = "test_df", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    conn = conn,
                                    verbose = 10
                                    )
        with self.assertRaises(Exception) as verbose:
            broken_verbose()
            
        self.assertTrue('Invalid input error. The verbose option must be'\
                        'the integer 0,1,2 or 3.'in str(verbose.exception))
                
    def test_false_max_depth(self):
        def broken_max_depth():
            res_post_new2 = FLAME_db(input_data = "test_df", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    conn = conn,
                                    max_depth = -10
                                    )
        with self.assertRaises(Exception) as max_depth:
            broken_max_depth()
            
        self.assertTrue('Invalid input error. The max_depth must be'\
                'a postive integer.'in str(max_depth.exception))
        
    def test_false_random_state(self):
        def broken_random_state():
            res_post_new2 = FLAME_db(input_data = "test_df", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    conn = conn,
                                    verbose = 3,
                                    random_state = -1000
                                    )
        with self.assertRaises(Exception) as random_state:
            broken_random_state()
            
        self.assertTrue('Invalid input error. The random_state  must be'\
                'a postive integer or None.'in str(random_state.exception))

        
        
    def test_false_missing_data_replace(self):
        def broken_missing_data_replace():
            res_post_new2 = FLAME_db(input_data = "test_df", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    conn = conn,
                                    verbose = 3,
                                    missing_data_replace =4
                                    )
        with self.assertRaises(Exception) as missing_data_replace:
            broken_missing_data_replace()
            
        self.assertTrue('Invalid input error. missing_data_replace value must '\
            'be 0, 1 or 2'in str(missing_data_replace.exception))
        
    def test_false_missing_holdout_replace(self):
        def broken_missing_holdout_replace():
            res_post_new2 = FLAME_db(input_data = "test_df", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    conn = conn,
                                    verbose = 3,
                                    missing_holdout_replace =4
                                    )
        with self.assertRaises(Exception) as missing_holdout_replace:
            broken_missing_holdout_replace()
            
        self.assertTrue('Invalid input error. missing_holdout_replace value must '\
            'be 0, or 1'in str(missing_holdout_replace.exception))
        
    
        
    def test_false_treatment_column_name_value(self):
        def broken_treatment_column_name_value():
            insert_data_to_db("test_df_t", # The name of your table containing the dataset to be matched
                                    data,
                                    treatment_column_name= "treated",
                                    outcome_column_name= 'outcome',conn = conn)
            df = holdout.copy()
            df.loc[0,'treated'] = 4
            res_post_new1 = FLAME_db(input_data = "test_df_t", # The name of your table containing the dataset to be matched
                                    holdout_data = df, # holdout set
                                    C = 0.1,
                                    conn = conn,
                                    matching_option = 0,
                                    verbose = 3,
                                    k = 0
                                    )
        with self.assertRaises(Exception) as treatment_column_name_value:
            broken_treatment_column_name_value()
        self.assertTrue('Invalid input error. All rows in the treatment '\
                        'column must have either a 0 or a 1 value.' in str(treatment_column_name_value.exception))
        
    def test_false_input_treatment_value(self):
        def broken_input_treatment_value():
            df = data.copy()
            df.loc[0,'treated'] = 4
            insert_data_to_db("test_df_treatment", # The name of your table containing the dataset to be matched
                    df,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn)
            
            res_post_new2 = FLAME_db(input_data = "test_df_treatment", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    conn = conn
                                    )
        with self.assertRaises(Exception) as input_treatment_value:
            broken_input_treatment_value()
            
        self.assertTrue('Invalid input error. All rows in the treatment '\
                        'column must have either a 0 or a 1 value.'in str(input_treatment_value.exception))
        
#        
