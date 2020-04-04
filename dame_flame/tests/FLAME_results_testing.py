# -*- coding: utf-8 -*-
"""
@author: Neha
"""
from . import dame_flame
import unittest
import pandas as pd

class TestFlame(unittest.TestCase):
    '''
    This file tests the overall FLAME algorithm against results that were 
    confirmed to be correct by comparing to the FLAME R package. 
    '''
    
    
    def test_large_C_repeats_F(self):
        
        result = dame_flame.DAME_FLAME.FLAME(
            input_data=r"../../dame_flame/data/data.csv",
            treatment_column_name='treated', outcome_column_name='outcome', 
            adaptive_weights='ridgeCV', 
            holdout_data=r"../../dame_flame/data/holdout.csv", repeats=False, 
            stop_unmatched_c=False, stop_unmatched_t=True, verbose=3))
        
        #self.assertEqual(match_ng(df,covs,covs_max_list, 'T'),
        #                 (array(match_indicator), array(matched_pair)))
                  
        
    def test_large_C_repeats_T(self):
        return
    
    def test_large_C_repeats_F_missing_replace_1(self):
        return
    
    def test_large_C_repeats_T_missing_replace_1(self):
        return
        
    def test_large_C_repeats_F_missing_replace_2(self):
        return
    
    def test_large_C_repeats_T_missing_replace_2(self):
        return
    
    # now consider something with low C to compare based on Pe? 

    """
    def test_proposition2_unedited(self):
        data = [[0,2,0],[1,1,0],[1,0,1],[1,1,1]]
        df = pd.DataFrame(data, columns=['first var', 'second var', 'T'])
        covs = ['first var', 'second var']
        covs_max_list = [2,3]
        
        # Changing the order from the above:
        df = df[['second var', 'first var', 'T']]
        covs.reverse()
        covs_max_list.reverse()
        
        match_indicator = [False, True, False, True]
        matched_pair = [4,4]
        
        print(match(df,covs,covs_max_list, 'T'))
        self.assertEqual(match(df,covs,covs_max_list, 'T'), 
                         (match_indicator, matched_pair))
    """


if __name__ == '__main__':
    unittest.main()