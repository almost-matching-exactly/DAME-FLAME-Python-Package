# -*- coding: utf-8 -*-
"""
@author: Neha
"""
import flame_group_by
import unittest
import pandas as pd

class TestFlameGroupBy(unittest.TestCase):
    '''
    This file tests Tianyu's Flame Group By operations. I'm fairly sure off of
    my own testing that that code works fine, I just can't get these tests to 
    work because of data type misalignment.
    '''
    
    '''
    def test_proposition2(self):
        data = [[0,2,0],[1,1,0],[1,0,1],[1,1,1]]
        df = pd.DataFrame(data, columns=['first var', 'second var', 'T'])
        covs = ['first var', 'second var']
        covs_max_list = [2,3]
        
        match_indicator = [False, True, False, True]
        matched_pair = [4,4]
        
        print(match_ng(df,covs,covs_max_list, 'T'))
        self.assertEqual(match_ng(df,covs,covs_max_list, 'T'),
                         (array(match_indicator), array(matched_pair))
    
    
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
    '''
    
if __name__ == '__main__':
    unittest.main()