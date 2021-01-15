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

p = 5
TE = 5
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

insert_data_to_db("test_df5", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn)
res_post_new1 = FLAME_db(input_data = "test_df5", # The name of your table containing the dataset to be matched
                        holdout_data = holdout, # holdout set
                        conn = conn,
                        matching_option = 3,
                        verbose = 3,
                        k = 0,
                        early_stop_un_c_frac = 1
                        )
insert_data_to_db("test_df6", # The name of your table containing the dataset to be matched
                    data,
                    treatment_column_name= "treated",
                    outcome_column_name= 'outcome',conn = conn)
res_post_new1 = FLAME_db(input_data = "test_df6", # The name of your table containing the dataset to be matched
                        holdout_data = holdout, # holdout set
                        conn = conn,
                        matching_option = 3,
                        verbose = 3,
                        k = 0,
                        early_stop_un_t_frac = 1
                        )
