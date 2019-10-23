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