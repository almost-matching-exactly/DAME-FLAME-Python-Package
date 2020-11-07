# -*- coding: utf-8 -*-
"""
@author: Neha
"""


from dame_flame import matching
import unittest
import pandas as pd
import os
import sys

class TestFlame(unittest.TestCase):
    '''
    This file tests the overall FLAME algorithm against results that were 
    confirmed to be correct by comparing to the FLAME R package. 
    '''
    
    def test_large_C_repeats_F(self):
        
        #df_path = (os.path.dirname(__file__))+"basicTestData.csv"
        #df = pd.read_csv(r"../data/basicTestData.csv")
        #df = pd.read_csv(df_path)
        
        #df = pd.read_csv(R"basicTestData.csv")
        
        
    
        df_path = os.path.join((os.path.dirname(__file__)), 'basicTestData.csv')
        df = pd.read_csv(df_path)
    
        holdout_path = os.path.join((os.path.dirname(__file__)), 'basicHoldoutData.csv')
        holdout = pd.read_csv(holdout_path)
        model = matching.FLAME(repeats=False, verbose=1)
        model.fit(holdout_data=holdout)
        algo_output = model.predict(df, C=100000)
        
        result_path = os.path.join((os.path.dirname(__file__)), 'basicResultData.csv')
        result = pd.read_csv(result_path, index_col="Unnamed: 0")
        
        dfs_equal = 1
        try:            
            for index in result.index:
                for col in result.columns:
                    if (result.loc[index, col] != "*" and 
                        algo_output.loc[index, col] != "*" and
                        int(result.loc[index, col]) != int(algo_output.loc[index, col])):
                            print("index, col", index, col)
                            dfs_equal = 0
                            break
        except (KeyError, ValueError):
            # We would hit this block if theres a key error, so df columns
            # are not equal or have different units, or weird entry in df, (string)
            dfs_equal = 0
        
        self.assertEqual(1, dfs_equal, 
                         msg='Data frames not equal on index {0}, col {1}'.format(index, col))
                          
    
#if __name__ == '__main__':
#    unittest.main()
    