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
        
