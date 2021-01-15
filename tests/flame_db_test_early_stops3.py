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


p = 4
TE = 5

data,weight_array = gen_data_db(n = 100,p = p, TE = TE)
holdout,weight_array = gen_data_db(n = 50,p = p, TE = TE)
data[data.loc[:,'treated'] ==1] = 0
data.loc[1,'treated'] = 1
#Connect to the database
select_db = "postgreSQL"  # Select the database you are using
database_name='tmp' # database name
host = 'localhost' #host ='vcm-17819.vm.duke.edu' # "127.0.0.1"
port = "5432"
user="postgres"
password= ""
conn = connect_db(database_name, user, password, host, port)
#insert_data_to_db("test_df1", # The name of your table containing the dataset to be matched
#                    data,
#                    treatment_column_name= "treated",
#                    outcome_column_name= 'outcome',conn = conn)
#res_post_new1 = FLAME_db(input_data = "test_df1", # The name of your table containing the dataset to be matched
#                        holdout_data = holdout, # holdout set
#                        treatment_column_name= "treated",
#                        outcome_column_name= 'outcome',
#                        C = 0.1,
#                        conn = conn,
#                        matching_option = 3,
#                        verbose = 3,
#                        k = 0
#                        )
#
#
#data.loc[:,'treated']= 1
#data.loc[1,'treated'] = 0
#insert_data_to_db("test_df2", # The name of your table containing the dataset to be matched
#                    data,
#                    treatment_column_name= "treated",
#                    outcome_column_name= 'outcome',conn = conn)
#res_post_new1 = FLAME_db(input_data = "test_df2", # The name of your table containing the dataset to be matched
#                        holdout_data = holdout, # holdout set
#                        treatment_column_name= "treated",
#                        outcome_column_name= 'outcome',
#                        C = 0.1,
#                        conn = conn,
#                        matching_option = 3,
#                        verbose = 3,
#                        k = 0
#                        )

p=10
data,weight_array = gen_data_db(n = 100,p = p, TE = TE)
holdout,weight_array = gen_data_db(n = 50,p = p, TE = TE)
insert_data_to_db("test_df3", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn)
res_post_new1 = FLAME_db(input_data = "test_df3", # The name of your table containing the dataset to be matched
                        holdout_data = holdout, # holdout set
                        conn = conn,
                        matching_option = 3,
                        verbose = 3,
                        k = 0,
                        early_stop_pe = 0.0
                        )

TE = 5

p=10
data,weight_array = gen_data_db(n = 100,p = p, TE = TE)
holdout,weight_array = gen_data_db(n = 50,p = p, TE = TE)
insert_data_to_db("test_df4", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn)
res_post_new1 = FLAME_db(input_data = "test_df4", # The name of your table containing the dataset to be matched
                        holdout_data = holdout, # holdout set
                        conn = conn,
                        matching_option = 3,
                        verbose = 3,
                        k = 0,
                        early_stop_iterations = 1
                        )
