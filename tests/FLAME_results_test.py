# -*- coding: utf-8 -*-
"""Testing file"""
# author: Neha Gupta, Duke University
# Copyright Duke University 2020
# License: MIT

from dame_flame import matching
from dame_flame.utils.data import *
from dame_flame.utils.post_processing import *
import unittest
import pandas as pd
import os
import sys

def check_statistics(model,unit_id = 1):
    ATE_ = ATE(model)
    ATT_ = ATT(model)
    MG_ = MG(model,unit_id)
    CATE_ = CATE(model,unit_id)
    
    if len(model.units_per_group) == 0:
        return True
    if len(model.groups_per_unit) == 0:
        return True
    if type(ATE_) == np.nan:
        print("ATE: " + str(ATE_))
        return True
    if type(ATT_) == np.nan:
        print("ATT:" + str(ATT_))
        return True
    return False

class TestFlame(unittest.TestCase):
    '''
    This file tests the overall FLAME algorithm against results that were
    confirmed to be correct by comparing to the FLAME R package.
    '''
    
    def test_large_C_repeats_F(self):
        
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
        
    def test_PE_F(self):
        for adaptive_weights in [False, 'ridge', 'decisiontree', 'ridgeCV','decisiontreeCV']: #
            is_correct = 1
            try:
                model = None
                if adaptive_weights == False:
                    df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
                                              num_cov=7, min_val=0,
                                              max_val=3, covar_importance=[4,3,2,1,0,0,0])
                    holdout, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
                                                          num_cov=7, min_val=0,
                                                              max_val=3, covar_importance=[4,3,2,1,0,0,0])
                    covar_importance = np.array([4,3,2,1,0,0,0])
                    weight_array = covar_importance/covar_importance.sum()
                    model = matching.FLAME(repeats=False, verbose=0,adaptive_weights =adaptive_weights)
                    model.fit(holdout_data=holdout,weight_array = list(weight_array))
                    output = model.predict(df)
                else:
                    df, true_TE = generate_uniform_given_importance()
                    holdout, true_TE = generate_uniform_given_importance()
                    model = matching.FLAME(repeats=False, verbose=0,adaptive_weights =adaptive_weights)
                    model.fit(holdout_data=holdout)
                    output = model.predict(df)

                if check_statistics(model):
                    is_correct = 0
                    

            except (KeyError, ValueError):
                is_correct = 0

            self.assertEqual(1, is_correct,
                             msg='FLAME-Error when we use PE method: {0} '.format(str(adaptive_weights)))

    def test_datasets_F(self):
        df_path = os.path.join((os.path.dirname(__file__)), 'basicTestData.csv')

        for gen in [generate_uniform_given_importance,generate_binomial_given_importance,generate_binomial_decay_importance,df_path]:
            is_correct = 1
            try:
                df = None
                holdout = None
                if type(gen) != str:
                    df, true_TE = gen()
                    holdout, true_TE = gen()
                else:
                    df  = gen
                    holdout = gen
                model = matching.FLAME(repeats=False)
                model.fit(holdout_data=holdout)
                output = model.predict(df)
            
                if check_statistics(model):
                    is_correct = 0
                    break

            except (KeyError, ValueError):
                is_correct = 0

            self.assertEqual(1, is_correct,
                             msg='FLAME-Error when we use the dataset generated by {0} '.format(str(gen)))
    
    def test_repeats_F(self):
        #Test other parameters
        df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
                                              num_cov=7, min_val=0,
                                              max_val=3, covar_importance=[4,3,2,1,0,0,0])
        holdout, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
                                              num_cov=7, min_val=0,
                                              max_val=3, covar_importance=[4,3,2,1,0,0,0])
        is_correct = 1
        try:
            model = matching.FLAME(repeats=True)
            model.fit(holdout_data=holdout)
            output = model.predict(df)
            if check_statistics(model):
                is_correct = 0
            
        except (KeyError, ValueError):
            is_correct = 0

        self.assertEqual(1, is_correct, msg='FLAME-Error when repeat = True')
        
    def test_verbose_F(self):
        #Test verbose
        df, true_TE = generate_uniform_given_importance()
        for verbose in [0,1,2,3]:
            is_correct = 1
            try:
                df, true_TE = generate_uniform_given_importance(num_control=1000, num_treated=1000,
                                                              num_cov=7, min_val=0,
                                                              max_val=3, covar_importance=[4,3,2,1,0,0,0])
                holdout, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
                                                      num_cov=7, min_val=0,
                                                          max_val=3, covar_importance=[4,3,2,1,0,0,0])
                covar_importance = np.array([4,3,2,1,0,0,0])
                weight_array = covar_importance/covar_importance.sum()
                model = matching.FLAME(missing_data_replace = 2, want_bf = True, verbose = verbose)
                model.fit(holdout_data=holdout)
                output = model.predict(df)
                model = matching.FLAME(repeats=True,verbose=verbose)
                model.fit(holdout_data=0.5)
                output = model.predict(df)
                if check_statistics(model):
                    is_correct = 0
                    break
            except (KeyError, ValueError):
                is_correct = 0

            self.assertEqual(1, is_correct, msg='FLAME-Error when verbose ={0}'.format(verbose))
            
        
    def test_data_split_F(self):
        #Test data split
        df, true_TE = generate_uniform_given_importance(num_control=3000, num_treated=3000)

        is_correct = 1
        try:
            for holdout in [0.3,0.5,0.7]:
                model = matching.FLAME(repeats=True)
                model.fit(holdout_data=holdout)
                output = model.predict(df)
                if check_statistics(model):
                    is_correct = 0
                    break
        except (KeyError, ValueError):
            is_correct = 0

        self.assertEqual(1, is_correct, msg='FLAME-Error when holdout = {0}'.format(holdout))

        
    def test_miss_data_F(self):
        is_correct = 1
        try:
            for missing_holdout_replace in [0,1,2]:
                for missing_data_replace in [0,1,2,3]:
                    df, true_TE = generate_uniform_given_importance(num_control=1000, num_treated=1000)
                    #Create missing df
                    m,n = df.shape
                    for i in range(int(m/100)):
                        for j in [0,int(n/2)]:
                            df.iloc[i,j] = np.nan
                    holdout = df.copy()

                    model = matching.FLAME(missing_holdout_replace = missing_holdout_replace,missing_data_replace=missing_data_replace )
                    model.fit(holdout_data=holdout)
                    output = model.predict(df)
                    if check_statistics(model):
                        is_correct = 0
                        break

        except (KeyError, ValueError):
            is_correct = 0
        self.assertEqual(1, is_correct, msg='FLAME-Error when do missing data'\
                             'handling with missing_holdout_replace = {0},missing_data_replace{1}'.format(missing_holdout_replace,missing_data_replace))
        
    def test_want_pebf_F(self):
        #Test
        df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
                                              num_cov=7, min_val=0,
                                              max_val=3, covar_importance=[4,3,2,1,0,0,0])
        holdout, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
                                              num_cov=7, min_val=0,
                                              max_val=3, covar_importance=[4,3,2,1,0,0,0])

        is_correct = 1
        try:
            for want_pe in [False, True]:
                for want_bf in [False, True]:
                    model = matching.FLAME(want_pe=want_pe,want_bf=want_bf)
                    model.fit(holdout_data=holdout)
                    output = model.predict(df)
                    if check_statistics(model) or (want_pe and len(model.pe_each_iter)==0) or (want_bf and len(model.bf_each_iter)==0):
                        is_correct = 0
                        break

        except (KeyError, ValueError):
            is_wrong = 0
        self.assertEqual(1, is_correct, msg='FLAME Error when want_pe = {0} want_bf = {1}'.format(str(want_pe),str(want_bf)))
        
    def test_pre_dame_F(self):
        df, true_TE = generate_uniform_given_importance(num_control=500, num_treated=500,
                                  num_cov=7, min_val=0,
                                  max_val=3, covar_importance=[4,3,2,1,0,0,0])
        holdout, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
                                              num_cov=7, min_val=0,
                                                  max_val=3, covar_importance=[4,3,2,1,0,0,0])
        is_correct = 1
        try:
            covar_importance = np.array([4,3,2,1,0,0,0])
            weight_array = covar_importance/covar_importance.sum()
            for x in [False, True]:
                for y in [False, True]:
                    model1 = matching.FLAME(repeats=x,want_pe = y, want_bf = y,verbose=0,adaptive_weights = False)
                    model1.fit(holdout_data=holdout,weight_array = list(weight_array))
                    output = model1.predict(df, pre_dame = True)
                    model2 = matching.FLAME(repeats=x, want_pe = y, want_bf = y,verbose=0,adaptive_weights = 'decisiontreeCV')
                    model2.fit(holdout_data=holdout)
                    output = model2.predict(df, pre_dame = True)

                    output = model2.predict(df, pre_dame = True)
                    if check_statistics(model1) or check_statistics(model2) :
                        is_correct = 0
                
        except (KeyError, ValueError):
            is_correct = 0

        self.assertEqual(1, is_correct,
                         msg='FLAME-Error when we use pre_dame')
        
    def test_other_param_F(self):
        is_correct = 1
        try:
            df, true_TE = generate_uniform_given_importance(num_control=1000, num_treated=1000,
                                                  num_cov=7, min_val=0,
                                                  max_val=3, covar_importance=[4,3,2,1,0,0,0])
            holdout, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
                                                  num_cov=7, min_val=0,
                                                      max_val=3, covar_importance=[4,3,2,1,0,0,0])
            
            model = matching.FLAME( early_stop_pe= 1, verbose=0)
            model.fit(holdout_data=holdout)
            output = model.predict(df)
            if check_statistics(model):
                is_correct = 0
#            model = matching.FLAME( stop_unmatched_c= True, verbose=0)
#            model.fit(holdout_data=holdout)
#            output = model.predict(df)
#            if check_statistics(model):
#                is_correct = 0
#            model = matching.FLAME(stop_unmatched_t= True, verbose=0)
#            model.fit(holdout_data=holdout)
#            output = model.predict(df)
#            if check_statistics(model):
#                is_correct = 0
            model = matching.FLAME(early_stop_un_c_frac = 0.5, verbose=0)
            model.fit(holdout_data=holdout)
            output = model.predict(df)
            if check_statistics(model):
                is_correct = 0
            model = matching.FLAME(early_stop_un_t_frac = 0.5, verbose=0)
            model.fit(holdout_data=holdout)
            output = model.predict(df)
            if check_statistics(model):
                is_correct = 0
            model = matching.FLAME(early_stop_iterations= 2, verbose=0)
            model.fit(holdout_data=holdout)
            output = model.predict(df)
            if check_statistics(model):
                is_correct = 0
                
        except (KeyError, ValueError):
            is_correct = 0
        self.assertEqual(1, is_correct, msg='FLAME-Error when other parameters')


class TestDame(unittest.TestCase):


            
    def test_PE_F(self):
        for adaptive_weights in [ 'ridge', 'decisiontree', 'ridgeCV','decisiontreeCV']: #False,
            is_correct = 1
            try:
                model = None
                if adaptive_weights == False:
                    df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
                                              num_cov=7, min_val=0,
                                              max_val=3, covar_importance=[4,3,2,1,0,0,0])
                    holdout, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
                                                          num_cov=7, min_val=0,
                                                              max_val=3, covar_importance=[4,3,2,1,0,0,0])
                    covar_importance = np.array([4,3,2,1,0,0,0])
                    weight_array = covar_importance/covar_importance.sum()
                    model = matching.DAME(repeats=False, verbose=0,adaptive_weights =adaptive_weights)
                    model.fit(holdout_data=holdout,weight_array = list(weight_array))
                    output = model.predict(df)
                else:
                    df, true_TE = generate_uniform_given_importance()
                    holdout, true_TE = generate_uniform_given_importance()
                    model = matching.DAME(repeats=False, verbose=0,adaptive_weights =adaptive_weights)
                    model.fit(holdout_data=holdout)
                    output = model.predict(df)

                if check_statistics(model):
                    is_correct = 0
                    break

            except (KeyError, ValueError):
                is_correct = 0


            self.assertEqual(1, is_correct,
                             msg='DAME-Error when we use PE method: {0} '.format(adaptive_weights))

    def test_datasets_F(self):
        df_path = os.path.join((os.path.dirname(__file__)), 'basicTestData.csv')
        for gen in [generate_uniform_given_importance,generate_binomial_given_importance,generate_binomial_decay_importance,df_path]:
            is_correct = 1
            try:
                df = None
                holdout = None
                if type(gen) != str:
                    df, true_TE = gen()
                    holdout, true_TE = gen()
                else:
                    df  = gen
                    holdout = gen
                model = matching.DAME(repeats=False)
                model.fit(holdout_data=holdout)
                output = model.predict(df)
                
                        
                if check_statistics(model):
                    is_correct = 0
                    break

            except (KeyError, ValueError):
                is_correct = 0

            self.assertEqual(1, is_correct,
                             msg='DAME-Error when we use the dataset generated by {0} '.format(str(gen)))
    
#     def test_repeats_F(self):
#         #Test other parameters
#         df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
#                                               num_cov=7, min_val=0,
#                                               max_val=3, covar_importance=[4,3,2,1,0,0,0])
#         holdout, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
#                                               num_cov=7, min_val=0,
#                                               max_val=3, covar_importance=[4,3,2,1,0,0,0])
#         is_correct = 1
#         try:
#             model = matching.DAME(repeats=True)
#             model.fit(holdout_data=holdout)
#             output = model.predict(df)
#             if check_statistics(model):
#                 is_correct = 0

#         except (KeyError, ValueError):
#             is_correct = 0

#         self.assertEqual(1, is_correct, msg='DAME-Error when repeat = True')
        
#    def test_verbose_F(self):
#        #Test verbose
#        df, true_TE = generate_uniform_given_importance()
#        for verbose in [0,1,2,3]:
#            is_correct = 1
#            try:
#                df, true_TE = generate_uniform_given_importance(num_control=1000, num_treated=1000,
#                                                              num_cov=7, min_val=0,
#                                                              max_val=3, covar_importance=[4,3,2,1,0,0,0])
#                holdout, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
#                                                      num_cov=7, min_val=0,
#                                                          max_val=3, covar_importance=[4,3,2,1,0,0,0])
#                covar_importance = np.array([4,3,2,1,0,0,0])
#                weight_array = covar_importance/covar_importance.sum()
#                model = matching.DAME(missing_data_replace = 2, want_bf = True, verbose = verbose)
#                model.fit(holdout_data=holdout)
#                output = model.predict(df)
#
#                model = matching.DAME(verbose=verbose) # repeats = True
#                model.fit(holdout_data=0.5)
#                output = model.predict(df)
#                if check_statistics(model):
#                    is_correct = 0
#                    break
#            except (KeyError, ValueError):
#                is_correct = 0
#
#            self.assertEqual(1, is_correct, msg='DAME-Error when verbose ={0}'.format(verbose))
            
        
    def test_data_split_F(self):
        #Test data split
        df, true_TE = generate_uniform_given_importance(num_control=3000, num_treated=3000)

        is_correct = 1
        try:
            for holdout in [0.3,0.5,0.7]:
                model = matching.DAME(repeats=True)
                model.fit(holdout_data=holdout)
                output = model.predict(df)
                if check_statistics(model):
                    is_correct = 0
                    break
        except (KeyError, ValueError):
            is_correct = 0

        self.assertEqual(1, is_correct, msg='DAME-Error when holdout = {0}'.format(holdout))

        
    def test_miss_data_F(self):

        is_correct = 1
        try:
            for missing_holdout_replace in [0,1,2]:
                for missing_data_replace in [0,1,2]:
                    #Test missig data handling
                    df, true_TE = generate_uniform_given_importance(num_control=1000, num_treated=1000)
                    #Create missing df
                    m,n = df.shape
                    for i in range(int(m/10)):
                        for j in [0,int(n/2)]:
                            df.iloc[i,j] = np.nan
                    holdout = df.copy()
                    model = matching.DAME(repeats = False,missing_holdout_replace = missing_holdout_replace,missing_data_replace=missing_data_replace )
                    model.fit(holdout_data=holdout)
                    output = model.predict(df)
                    if check_statistics(model):
                        is_correct = 0
                        break

        except (KeyError, ValueError):
            is_correct = 0
        self.assertEqual(1, is_correct, msg='DAME-Error when do missing data'\
                             'handling with missing_holdout_replace = {0},missing_data_replace{1}'.format(missing_holdout_replace,missing_data_replace))
        
    def test_want_pebf_F(self):
        #Test
        df, true_TE = generate_uniform_given_importance(num_control=3000, num_treated=3000,
                                              num_cov=6, min_val=0,
                                              max_val=3, covar_importance=[4,3,2,1,0,0])
        holdout, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
                                              num_cov=6, min_val=0,
                                              max_val=3, covar_importance=[4,3,2,1,0,0])

        is_correct = 1
        try:
            for want_pe in [False, True]:
                for want_bf in [False, True]:
                    model = matching.DAME(want_pe=want_pe,want_bf=want_bf)
                    model.fit(holdout_data=holdout)
                    output = model.predict(df)
                    if check_statistics(model) or (want_pe and len(model.pe_each_iter)==0) or (want_bf and len(model.bf_each_iter)==0):
                        is_correct = 0
                        break

        except (KeyError, ValueError):
            is_correct = 0
        self.assertEqual(1, is_correct, msg='DAME Error when want_pe = {0} want_bf = {1}'.format(str(want_pe),str(want_bf)))
        
    def test_other_param_F(self):
        is_correct = 1
        try:
            df, true_TE = generate_uniform_given_importance(num_control=1000, num_treated=1000,
                                                  num_cov=7, min_val=0,
                                                  max_val=3, covar_importance=[4,3,2,1,0,0,0])
            holdout, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
                                                  num_cov=7, min_val=0,
                                                      max_val=3, covar_importance=[4,3,2,1,0,0,0])

            model = matching.DAME( early_stop_pe= 1, verbose=0)
            model.fit(holdout_data=holdout)
            output = model.predict(df)
            if check_statistics(model):
                is_correct = 0
#            model = matching.DAME( stop_unmatched_c= True, verbose=0)
#            model.fit(holdout_data=holdout)
#            output = model.predict(df)
#            if check_statistics(model):
#                is_correct = 0
#            model = matching.DAME(stop_unmatched_t= True, verbose=0)
#            model.fit(holdout_data=holdout)
#            output = model.predict(df)
#            if check_statistics(model):
#                is_correct = 0
            model = matching.DAME(early_stop_un_c_frac = 0.5, verbose=0)
            model.fit(holdout_data=holdout)
            output = model.predict(df)
            if check_statistics(model):
                is_correct = 0
            model = matching.DAME(early_stop_un_t_frac = 0.5, verbose=0)
            model.fit(holdout_data=holdout)
            output = model.predict(df)
            if check_statistics(model):
                is_correct = 0
            model = matching.DAME(early_stop_iterations= 2, verbose=0)
            model.fit(holdout_data=holdout)
            output = model.predict(df)
            if check_statistics(model):
                is_correct = 0

        except (KeyError, ValueError):
            is_correct = 0
        self.assertEqual(1, is_correct, msg='DAME-Error when other parameters')















class Test_exceptions(unittest.TestCase):
    
    def test_false_dataset(self):
        def broken_false_dataset():
            df, true_TE = generate_uniform_given_importance(num_control=1000, num_treated=1000)
            holdout, true_TE = generate_uniform_given_importance(num_control=1000, num_treated=1000)
            model = matching.FLAME()
            model.fit(holdout_data=holdout)
            output = model.predict(False)

            
        with self.assertRaises(Exception) as false_dataset:
            broken_false_dataset()
            
        self.assertTrue("Need to specify either csv file name or pandas data "\
                        "frame in parameter 'input_data'" in str(false_dataset.exception))
        
    def test_false_early_stop_un_t_frac(self):
        def broken_early_stop_un_t_frac():
            df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100)
            model = matching.FLAME(early_stop_un_t_frac = -1)
            model.fit(holdout_data=df)
            output = model.predict(df)

        with self.assertRaises(Exception) as early_stop_un_t_frac:
            broken_early_stop_un_t_frac()
            
        self.assertTrue('The value provided for the early stopping critera '\
                        'of proportion of unmatched treatment units needs to '\
                        'be between 0.0 and 1.0' in str(early_stop_un_t_frac.exception))
    
    def test_false_early_stop_un_c_frac(self):
        def broken_early_stop_un_c_frac():
            df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100)
            model = matching.FLAME(early_stop_un_c_frac = -1)
            model.fit(holdout_data=df)
            output = model.predict(df)

        with self.assertRaises(Exception) as early_stop_un_c_frac:
            broken_early_stop_un_c_frac()
            
        self.assertTrue('The value provided for the early stopping critera '\
                        'of proportion of unmatched control units needs to '\
                        'be between 0.0 and 1.0' in str(early_stop_un_c_frac.exception))
        
        
    def test_false_early_stop_iterations(self):
        def broken_early_stop_iterations():
            df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100)
            model = matching.FLAME(early_stop_iterations = True)
            model.fit(holdout_data=df)
            output = model.predict(df)

        with self.assertRaises(Exception) as early_stop_iterations:
            broken_early_stop_iterations()
            
        self.assertTrue('The value provided for early_stop_iteration needs '\
                        'to be an integer number of iterations, or False if '\
                        'not stopping early based on the number of iterations' in str(early_stop_iterations.exception))
    def test_false_early_stop_pe_frac(self):
        def broken_early_stop_pe_frac():
            df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100)
            model = matching.FLAME(early_stop_pe_frac = 123)
            model.fit(holdout_data=df)
            output = model.predict(df)

        with self.assertRaises(Exception) as early_stop_pe_frac:
            broken_early_stop_pe_frac()
            
        self.assertTrue('The value provided for the early stopping critera of'\
                        ' PE needs to be between 0.0 and 1.0' in str(early_stop_pe_frac.exception))

#     def test_false_verbose(self):
#         def broken_verbose():
#             df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100)
#             model = matching.FLAME(verbose = 12312)
#             model.fit(holdout_data=df)
#             output = model.predict(df)

#         with self.assertRaises(Exception) as verbose:
#             broken_verbose()
            
#         self.assertTrue('Invalid input error. The verbose option must be'\
#                         'the integer 0,1,2 or 3.' in str(verbose.exception))
    def test_false_weight_array_type(self):
        def broken_weight_array_type():
            df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100)
            model = matching.FLAME(adaptive_weights = False)
            model.fit(holdout_data=df, weight_array = np.array([1,2,3,4,5]))
            output = model.predict(df)

        with self.assertRaises(Exception) as weight_array_type:
            broken_weight_array_type()
            
        self.assertTrue('Invalid input error. A weight array of type'\
                            'array needs to be provided when the'\
                            'parameter adaptive_weights == True' in str(weight_array_type.exception))

    def test_false_weight_array_len(self):
        def broken_weight_array_len():
            df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100)
            model = matching.FLAME(adaptive_weights = False)
            model.fit(holdout_data=df, weight_array = [1])
            output = model.predict(df)

        with self.assertRaises(Exception) as weight_array_len:
            broken_weight_array_len()
            
        self.assertTrue('Invalid input error. Weight array size not equal'\
                            ' to number of columns in dataframe' in str(weight_array_len.exception))
        
        
    def test_false_weight_array_sum(self):
        def broken_weight_array_sum():
            df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100)
            model = matching.FLAME(adaptive_weights = False)
            model.fit(holdout_data=df, weight_array = [1,1,1,1])
            output = model.predict(df)

        with self.assertRaises(Exception) as weight_array_sum:
            broken_weight_array_sum()
            
        self.assertTrue('Invalid input error. Weight array values must '\
                            'sum to 1.0' in str(weight_array_sum.exception))
        
        
        
    def test_false_alpha(self):
        def broken_alpha():
            df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100)
            model = matching.FLAME(adaptive_weights = 'ridge',alpha = -10)
            model.fit(holdout_data=df)
            output = model.predict(df)

        with self.assertRaises(Exception) as alpha:
            broken_alpha()
            
        self.assertTrue('Invalid input error. The alpha needs to be '\
                            'positive for ridge regressions.' in str(alpha.exception))
        
    def test_false_adaptive_weights(self):
        def broken_adaptive_weights():
            df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100)
            model = matching.FLAME(adaptive_weights = 'safdsaf')
            model.fit(holdout_data=df)
            output = model.predict(df)

        with self.assertRaises(Exception) as adaptive_weights:
            broken_adaptive_weights()
            
        self.assertTrue("Invalid input error. The acceptable values for "\
                            "the adaptive_weights parameter are 'ridge', "\
                            "'decisiontree', 'decisiontreeCV', or 'ridgeCV'. Additionally, "\
                            "adaptive-weights may be 'False' along "\
                            "with a weight array" in str(adaptive_weights.exception))
        
    def test_false_data_len(self):
        def broken_data_len():
            df, true_TE = generate_uniform_given_importance(num_control=1000, num_treated=1000,
                                                  num_cov=7, min_val=0,
                                                  max_val=3, covar_importance=[4,3,2,1,0,0,0])
            holdout, true_TE = generate_uniform_given_importance()
            model = matching.FLAME()
            model.fit(holdout_data=holdout)
            output = model.predict(df)

        with self.assertRaises(Exception) as data_len:
            broken_data_len()
            
        self.assertTrue('Invalid input error. The holdout and main '\
                            'dataset must have the same number of columns' in str(data_len.exception))
    
    def test_false_column_match(self):
        def broken_column_match():
            df, true_TE = generate_uniform_given_importance()
            holdout, true_TE = generate_uniform_given_importance()
            set_ = holdout.columns
            set_ = list(set_)
            set_[0] = 'dasfadf'
            holdout.columns  = set_
            model = matching.FLAME()
            model.fit(holdout_data=holdout)
            output = model.predict(df)

        with self.assertRaises(Exception) as column_match:
            broken_column_match()
            
        self.assertTrue('Invalid input error. The holdout and main '\
                            'dataset must have the same columns' in str(column_match.exception))
    def test_false_C(self):
        def broken_C():
            df, true_TE = generate_uniform_given_importance()
            holdout, true_TE = generate_uniform_given_importance()

            model = matching.FLAME()
            model.fit(holdout_data=holdout)
            output = model.predict(df,C = -1)

        with self.assertRaises(Exception) as C:
            broken_C()
            
        self.assertTrue('The C, or the hyperparameter to trade-off between'\
                           ' balancing factor and predictive error must be '\
                           ' nonnegative. 'in str(C.exception))
    def test_false_missing_data_replace(self):
        def broken_missing_data_replace():
                df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
                                                              num_cov=7, min_val=0,
                                                              max_val=3, covar_importance=[4,3,2,1,0,0,0])
                holdout, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100,
                                                      num_cov=7, min_val=0,
                                                          max_val=3, covar_importance=[4,3,2,1,0,0,0])
                covar_importance = np.array([4,3,2,1,0,0,0])
                weight_array = covar_importance/covar_importance.sum()
                model = matching.FLAME(missing_data_replace = 2, adaptive_weights =False)
                model.fit(holdout_data=holdout,weight_array = list(weight_array))
                output = model.predict(df)

        with self.assertRaises(Exception) as missing_data_replace:
            broken_missing_data_replace()
            
        self.assertTrue('Invalid input error. We do not support missing data '\
                        'handing in the fixed weights version of algorithms'in str(missing_data_replace.exception))
        
    def test_false_treatment_column_name(self):
        def broken_treatment_column_name():
            df, true_TE = generate_uniform_given_importance()
            holdout, true_TE = generate_uniform_given_importance()
            model = matching.FLAME()
            model.fit(holdout_data=holdout,treatment_column_name =  "sadfdag")
            output = model.predict(df)

        with self.assertRaises(Exception) as treatment_column_name:
            broken_treatment_column_name()
            
        self.assertTrue('Invalid input error. Treatment column name does not'\
                        ' exist' in str(treatment_column_name.exception))

    def test_false_outcome_column_name(self):
        def broken_outcome_column_name():
            df, true_TE = generate_uniform_given_importance()
            holdout, true_TE = generate_uniform_given_importance()
            model = matching.FLAME()
            model.fit(holdout_data=holdout,outcome_column_name =  "sadfdag")
            output = model.predict(df)

        with self.assertRaises(Exception) as outcome_column_name:
            broken_outcome_column_name()
            
        self.assertTrue('Invalid input error. Outcome column name does not'\
                        ' exist' in str(outcome_column_name.exception))
        
    def test_false_treatment_column_name_value(self):
        def broken_treatment_column_name_value():
            df, true_TE = generate_uniform_given_importance()
            holdout, true_TE = generate_uniform_given_importance()
            df.loc[0,'treated'] = 4
            model = matching.FLAME()
            model.fit(holdout_data=holdout)
            output = model.predict(df)

        with self.assertRaises(Exception) as treatment_column_name_value:
            broken_treatment_column_name_value()
        self.assertTrue('Invalid input error. All rows in the treatment '\
                        'column must have either a 0 or a 1 value.' in str(treatment_column_name_value.exception))
        

#     def test_false_weight_array_order(self):
#         def broken_weight_array_sum():
#             df, true_TE = generate_uniform_given_importance(num_control=100, num_treated=100)
#             model = matching.FLAME(adaptive_weights = False)
#             model.fit(holdout_data=df, weight_array = [1,1,1,1])
#             output = model.predict(df)

#         with self.assertRaises(Exception) as weight_array_sum:
#             broken_weight_array_sum()
            
#         self.assertTrue('Invalid input error. Weight array values must '\
#                             'sum to 1.0' in str(weight_array_sum.exception))
        
