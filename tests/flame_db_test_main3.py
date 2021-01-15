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
select_db = "MySQL"  # Select the database you are using
database_name='tmp' # database name
host = 'localhost' #host ='vcm-17819.vm.duke.edu' # "127.0.0.1"
port = "5432"
user="root"
password= ""
conn = connect_db(database_name, user, password, host, port,select_db = "MySQL")
#Insert the data into database

#
class TestFlame_db(unittest.TestCase):
              
    def test_MySQL(self):
        is_corrct = 1
        try:
        
            insert_data_to_db("test_df1000", # The name of your table containing the dataset to be matched
                        data,
                        treatment_column_name= "treated",
                        outcome_column_name= 'outcome',conn = conn)
            res_post_new1 = FLAME_db(input_data = "test_df1000", # The name of your table containing the dataset to be matched
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


            if check_statistics(res_post_new1):  #or check_statistics(res_post_new2):
                is_corrct = 0

        except (KeyError, ValueError):
                is_corrct = 0

        self.assertEqual(1, is_corrct,
                             msg='Error when test MySQL')

