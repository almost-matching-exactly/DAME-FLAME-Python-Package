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
insert_data_to_db("test_df100", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn)
insert_data_to_db("test_df101", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn)
class TestFlame_db(unittest.TestCase):
              
    def test_weights(self):
        is_corrct = 1
        try:
            res_post_new1 = FLAME_db(input_data = "test_df100", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout, # holdout set
                                    treatment_column_name= "treated",
                                    outcome_column_name= 'outcome',
                                    adaptive_weights = 'ridge',
                                    C = 0.1,
                                    conn = conn,
                                    matching_option = 0,
                                    verbose = 3,
                                    k = 0
                                    )
            holdout_path = os.path.join((os.path.dirname(__file__)), 'holdout.csv')
            
            res_post_new1 = FLAME_db(input_data = "test_df101", # The name of your table containing the dataset to be matched
                                    holdout_data = holdout_path, # holdout set
                                    treatment_column_name= "treated",
                                    outcome_column_name= 'outcome',
                                    C = 0.1,
                                    conn = conn,
                                    matching_option = 0,
                                    verbose = 3,
                                    k = 0
                                    )
            if check_statistics(res_post_new1):  #or check_statistics(res_post_new2):
                is_corrct = 0
            
        except (KeyError, ValueError):
                is_corrct = 0

        self.assertEqual(1, is_corrct,
                             msg='Error when test weights')
                             
#    def test_MySQL(self):
#        is_corrct = 1
#        try:
#            # Select the database you are using
#            database_name='tmp' # database name
#            host ='vcm-17819.vm.duke.edu' # "127.0.0.1"
#            port = "5432"
#            user="newuser"
#            password= "sunxian123"
#            conn = connect_db(database_name, user, password, host, port, select_db = "MySQL")
#            #Insert the data into database
#
#            insert_data_to_db("test_df101", # The name of your table containing the dataset to be matched
#                                data,
#                                treatment_column_name= "treated",
#                                outcome_column_name= 'outcome',conn = conn)
#            res_post_new1 = FLAME_db(input_data = "test_df100", # The name of your table containing the dataset to be matched
#                                    holdout_data = holdout, # holdout set
#                                    treatment_column_name= "treated",
#                                    outcome_column_name= 'outcome',
#                                    adaptive_weights = 'ridge',
#                                    C = 0.1,
#                                    conn = conn,
#                                    matching_option = 0,
#                                    verbose = 3,
#                                    k = 0
#                                    )
#
#
#            if check_statistics(res_post_new1):  #or check_statistics(res_post_new2):
#                is_corrct = 0
#            
#        except (KeyError, ValueError):
#                is_corrct = 0
#
#        self.assertEqual(1, is_corrct,
#                             msg='Error when test MySQL')

                    
                    
                    
#    def test_missing_datasets(self):
#        is_corrct = 1
#        try:
#
#            holdout_miss = holdout.copy()
#            m,n = holdout_miss.shape
#            for i in range(int(m/100)):
#                for j in [0,int(n/2)]:
#                    holdout_miss.iloc[i,j] = np.nan
#            res_post_new = FLAME_db(input_data = "test_df100", # The name of your table containing the dataset to be matched
#                                    holdout_data = holdout_miss, # holdout set
#                                    C = 0,
#                                    conn = conn,
#                                    matching_option = 2,
#                                    adaptive_weights = 'decisiontree',
#                                    verbose = 1,
#                                    missing_data_replace = 0,
#                                    missing_holdout_replace = 0)
#            if check_statistics(res_post_new):
#                is_corrct = 0
#
#        except (KeyError, ValueError):
#                is_corrct = 0
#
#        self.assertEqual(1, is_corrct,
#                             msg='Error when test missing datasets')


