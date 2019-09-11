# -*- coding: utf-8 -*-
"""
@author: Neha
"""

import dame_algorithm
import unittest
import pandas as pd

class TestAlgorithm3(unittest.TestCase):

    def test_case1(self):
        '''
        This case aims to test an example pf two possible covariates and 4 
        units. Where two items are an exact match on all covariates, 
        and then when using only one covariate to match on, 3 form a group but
        one has no group.
        '''
        # TODO: confirm this one. You can have no group, right?
        file_name = 'sample.csv'
        df = pd.read_csv(file_name)
        weight_array = [0.75, 0.25]
        treatment_column_name = 'treated'
        outcome_column_name='outcome'
        
        covs_list = [['1', '2'], 
                            ['1']]
        matched_group =  [[1, 1], [1, '*']]
        matched_data = [(1, 0), (3, 0), (1, 1), (2, 1), (3, 1)]
        expected = (covs_list, matched_group, matched_data)
        
        #rcovs_list = [['first variable', 'second variable'], 
        #                    ['second variable']]
        #rmatched_group =  [[1, 1], ['*', 1]]
        #rmatched_data = [(1, 0), (3, 0), (1, 1), (3, 1)]
        #expected = (rcovs_list, rmatched_group, rmatched_data)
        
            
        self.assertEqual(dame_algorithm.algo1(df,
                                              treatment_column_name,
                                              weight_array,
                                              outcome_column_name), expected)
  
    def test_case2(self):
        '''
        This case aims to test an example of two possible covariates and 4 
        units. two items are an exact match on all covariates, and then when 
        using only one covariate to match on, all 4 form a group.
        '''
        file_name = 'sample2.csv'
        df = pd.read_csv(file_name)
        weight_array = [0.75, 0.25]
        treatment_column_name = 'T'
        outcome_column_name='outcome'
        
        covs_list = [['first variable', 'second variable'], 
                            ['first variable']]
        matched_group =  [[1, 1], [1, '*']]
        
        # TODO: confirm that this output will always be in this order. If not,
        # would have to change the data type to a dict: key=groupnum, val=set.
        matched_data = [(1, 0), (3, 0), (0,1), (1, 1), (2, 1), (3, 1)]
        
        expected = (covs_list, matched_group, matched_data)
            
        self.assertEqual(dame_algorithm.algo1(df,
                                              treatment_column_name,
                                              weight_array,
                                              outcome_column_name), expected)
        
    def test_case3(self):
        '''
        This case aims to test an example of two possible covariates and 4 
        units. two items are an exact match on all covariates, and then when 
        using only one covariate to match on, all 4 form a group.
        '''
        file_name = 'sample2.csv'
        df = pd.read_csv(file_name)
        weight_array = [0.25, 0.75]
        treatment_column_name = 'T'
        outcome_column_name='outcome'
        
        covs_list = [['first variable', 'second variable'], 
                            ['second variable'], ['first variable']]
        matched_group =  [[1, 1], ['*', 1],[1,'*']]
        
        matched_data = [(1, 0), (3, 0), (1,1), (3,1), (0,2), (1, 2), (2, 2), 
                        (3, 2)]
        
        expected = (covs_list, matched_group, matched_data)
            
        self.assertEqual(dame_algorithm.algo1(df,
                                              treatment_column_name,
                                              weight_array,
                                              outcome_column_name), expected)
        
#    def test_case4(self):
        '''
        This case is a column longer than the others.
        
        file_name = 'sample4.csv'
        df = pd.read_csv(file_name)
        weight_array = [0.25, 0.05, 0.7]
        treatment_column_name = 'T'
        outcome_column_name='outcome'
        
        covs_list = [['first variable', 'no2', 'other variable'],
                     ['first variable', 'other variable'],
                     ['no2', 'other variable'],
                     ['no2', 'first variable']]
        matched_group =  [['*', 1, 1], [0, 1, '*'], [1, 1, '*']]
        
        matched_data = [(1, 0), (3, 0), (1, 1), (2, 1), (0, 2), (3, 2)]
        
        expected = (covs_list, matched_group, matched_data)
            
        self.assertEqual(dame_algorithm.algo1(df,
                                              treatment_column_name,
                                              weight_array,
                                              outcome_column_name), expected)
       ''' 
if __name__ == '__main__':
    unittest.main()