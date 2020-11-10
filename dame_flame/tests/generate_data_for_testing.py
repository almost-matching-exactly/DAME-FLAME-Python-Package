# -*- coding: utf-8 -*-
"""
@author: Neha

This file exists to create data that fits a particular distribution so that
I can do some testing and make sure matches look as expected. 

"""
import pandas as pd
import numpy as np

def create_data():
    
    df = pd.DataFrame(columns=['a', 'b', 'c', 'd', 'e', 'treated', 'outcome'])
    
    # insert 100 control units with randomly chosen outcome values:
    
    control_values = [1,2,3,4,5]
    treat_values = [2,3,4,5,6]
    for i in range(20):
        
        if i < 10:
            df.loc[i] = control_values + [0] + list(np.random.normal(loc=0, size=1))
        else:
            df.loc[i] = treat_values + [1] + list(np.random.normal(loc=1, size=1))
            
    return df

# Get 1000 rows of data chopped up from the 30k one. Add a few columns so its 
# 20 columns instead of 15
    
def create_1k():
    old = pd.read_csv('old-dame-code-input-df.csv')
    old_holdout = pd.read_csv('old-dame-code-input-holdout.csv')
    df = pd.DataFrame(columns=['0',	'1',	'2'	, '3',	'4',	'5',	'6'	, '7', \
                               '8',	'9', 	\
                               'outcome', 	'treated'])
    df_holdout = pd.DataFrame(columns=['0',	'1',	'2'	, '3',	'4',	'5',	'6'	, '7', \
                               '8',	'9', 	\
                               'outcome', 	'treated'])
    for i in range(1000):
        # randomly grab a number from 0 to 30,000 to read in. 
        #try:
        df.loc[i] = old.loc[random.randrange(0,30000)]
        df_holdout.loc[i] = old_holdout.loc[random.randrange(0,30000)]
        #except KeyError:
        #    continue 
        
    return df, df_holdout

df=create_data()
print (df)