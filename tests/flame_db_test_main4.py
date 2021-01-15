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
gen_data_db(n = 100,p = 2, TE = TE)
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
#Insert the data into database
insert_data_to_db("test_df400", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn, add_missing = True)
#Insert the data into database
insert_data_to_db("test_df401", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn, add_missing = True)
insert_data_to_db("test_df402", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn, add_missing = True)
class TestFlame_db(unittest.TestCase):
              
    def test_missing(self):
        is_corrct = 1
        try:

            res_post_new2 = FLAME_db(input_data = "test_df400", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    treatment_column_name= "treated",
                                    outcome_column_name= 'outcome',
                                    C = 0.1,
                                    conn = conn,
                                    matching_option = 2,
                                    verbose = 3,
                                    k = 0
                                    )
            if  check_statistics(res_post_new2):
                is_corrct = 0
            
        except (KeyError, ValueError):
                is_corrct = 0

        self.assertEqual(1, is_corrct,
                             msg='Error when missing data in database')
                             
    def test_missing2(self):
        is_corrct = 1
        try:
            res_post_new2 = FLAME_db(input_data = "test_df401", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    treatment_column_name= "treated",
                                    outcome_column_name= 'outcome',
                                    C = 0.1,
                                    conn = conn,
                                    matching_option = 2,
                                    missing_data_replace = 1,
                                    verbose = 3,
                                    k = 0
                                    )
            if  check_statistics(res_post_new2):
                is_corrct = 0
            
        except (KeyError, ValueError):
                is_corrct = 0

        self.assertEqual(1, is_corrct,
                             msg='Error when missing data in database')



    def test_weights(self):
        is_corrct = 1
        try:
            res_post_new2 = FLAME_db(input_data = "test_df402", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    treatment_column_name= "treated",
                                    outcome_column_name= 'outcome',
                                    C = 0.1,
                                    conn = conn,
                                    matching_option = 2,
                                    adaptive_weights = False,
                                    weight_array = weight_array,
                                    verbose = 3,
                                    k = 0
                                    )
            if  check_statistics(res_post_new2):
                is_corrct = 0
            
        except (KeyError, ValueError):
                is_corrct = 0

        self.assertEqual(1, is_corrct,
                             msg='Error when test weights')


