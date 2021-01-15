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


p = 3
TE = 5
gen_data_db(n = 100,p = 2, TE = TE)
data,weight_array = gen_data_db(n = 100,p = p, TE = TE)
holdout,weight_array = gen_data_db(n = 50,p = p, TE = TE)

#Connect to the database
select_db = "postgreSQL"  # Select the database you are using
database_name='tmp' # database name
host = 'localhost' #host ='vcm-17819.vm.duke.edu' # "127.0.0.1"
port = "5432"
user="postgres"
password= ""
conn = connect_db(database_name, user, password, host, port)


class Test_exceptions(unittest.TestCase):
    
    def test_false_dataset(self):
        def broken_false_dataset():
            insert_data_to_db("test_df30", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn)
            res_post_new1 = FLAME_db(input_data = data, # The name of your table containing the dataset to be matched
                                                holdout_data = holdout, # holdout set
                                                C = 0.1,
                                                conn = conn,
                                                matching_option = 0,
                                                verbose = 3,
                                                k = 0
                                                )
        with self.assertRaises(Exception) as false_dataset:
            broken_false_dataset()
            
        self.assertTrue("Need to specify the name of the table that contains the dataset in your database "\
                        "frame in parameter 'input_data'" in str(false_dataset.exception))
        
    def test_false_holdout(self):
        def broken_false_holdout():
            insert_data_to_db("test_df30", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn)
            res_post_new1 = FLAME_db(input_data = "test_df30", # The name of your table containing the dataset to be matched
                                                holdout_data = 0, # holdout set
                                                C = 0.1,
                                                conn = conn,
                                                matching_option = 0,
                                                verbose = 3,
                                                k = 0
                                                )
        with self.assertRaises(Exception) as holdout:
            broken_false_holdout()
            
        self.assertTrue("Holdout_data shoule be a dataframe or a directory" in str(holdout.exception))

        
    def test_false_treatment_column_name(self):
        def broken_treatment_column_name():
            insert_data_to_db("test_df31", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn)
            res_post_new1 = FLAME_db(input_data = "test_df31", # The name of your table containing the dataset to be matched
                                                holdout_data = holdout, # holdout set
                                                treatment_column_name= "sadfdag",
                                                C = 0.1,
                                                conn = conn,
                                                matching_option = 0,
                                                verbose = 3,
                                                k = 0
                                                )
        with self.assertRaises(Exception) as treatment_column_name:
            broken_treatment_column_name()
            
        self.assertTrue('Invalid input error. Treatment column name does not'\
                        ' exist' in str(treatment_column_name.exception))

    def test_false_outcome_column_name(self):
        def broken_outcome_column_name():
            insert_data_to_db("test_df32", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn)
            res_post_new1 = FLAME_db(input_data = "test_df32", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    outcome_column_name= '1232114',
                                    C = 0.1,
                                    conn = conn,
                                    matching_option = 0,
                                    verbose = 3,
                                    k = 0
                                    )

        with self.assertRaises(Exception) as outcome_column_name:
            broken_outcome_column_name()
            
        self.assertTrue('Invalid input error. Outcome column name does not'\
                        ' exist' in str(outcome_column_name.exception))
        

        
    def test_false_early_stop_un_t_frac(self):
        def broken_early_stop_un_t_frac():
            insert_data_to_db("test_df33", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn)
            res_post_new1 = FLAME_db(input_data = "test_df33", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    C = 0.1,
                                    conn = conn,
                                    matching_option = 0,
                                    verbose = 3,
                                    early_stop_un_t_frac = -1,
                                    k = 0
                                    )

        with self.assertRaises(Exception) as early_stop_un_t_frac:
            broken_early_stop_un_t_frac()

        self.assertTrue('The value provided for the early stopping critera '\
                        'of proportion of unmatched treatment units needs to '\
                        'be between 0.0 and 1.0' in str(early_stop_un_t_frac.exception))

    def test_false_early_stop_un_c_frac(self):
        def broken_early_stop_un_c_frac():
            insert_data_to_db("test_df34", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn)
            res_post_new1 = FLAME_db(input_data = "test_df34", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    C = 0.1,
                                    conn = conn,
                                    matching_option = 0,
                                    verbose = 3,
                                    early_stop_un_c_frac=-1,
                                    k = 0
                                    )

        with self.assertRaises(Exception) as early_stop_un_c_frac:
            broken_early_stop_un_c_frac()

        self.assertTrue('The value provided for the early stopping critera '\
                        'of proportion of unmatched control units needs to '\
                        'be between 0.0 and 1.0' in str(early_stop_un_c_frac.exception))


    def test_false_early_stop_pe(self):
        def broken_early_stop_pe():
            insert_data_to_db("test_df35", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn)
            res_post_new1 = FLAME_db(input_data = "test_df35", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    C = 0.1,
                                    conn = conn,
                                    matching_option = 0,
                                    verbose = 3,
                                    early_stop_pe = -10,
                                    k = 0
                                    )

        with self.assertRaises(Exception) as early_stop_pe:
            broken_early_stop_pe()

        self.assertTrue('The value provided for the early stopping critera '\
                        'of PE needs to be non-negative ' in str(early_stop_pe.exception))

    def test_false_early_stop_pe_frac(self):
        def broken_early_stop_pe_frac():
            insert_data_to_db("test_df36", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn)
            res_post_new1 = FLAME_db(input_data = "test_df36", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    C = 0.1,
                                    conn = conn,
                                    matching_option = 0,
                                    verbose = 3,
                                    early_stop_pe_frac=-1,
                                    k = 0
                                    )

        with self.assertRaises(Exception) as early_stop_pe_frac:
            broken_early_stop_pe_frac()

        self.assertTrue('The value provided for the early stopping critera of'\
                        ' proportion of PE needs to be between 0.0 and 1.0' in str(early_stop_pe_frac.exception))
                        
    def test_false_select_database(self):
        def broken_select_database():
            conn = connect_db(database_name, user, password, host, port,select_db = "WRONG")

        with self.assertRaises(Exception) as select_database:
            broken_select_database()

        self.assertTrue("please select the database you are using " in str(select_database.exception))
                        

