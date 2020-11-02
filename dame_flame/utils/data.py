# -*- coding: utf-8 -*-
"""
Created on Sun Oct 25 13:59:18 2020
@author: Neha
"""

import pandas as pd
import numpy as np

def generate_uniform_given_importance(num_control=1000, num_treated=1000, 
                                      num_cov=4, min_val=0,
                                      max_val=3, covar_importance=[4,3,2,1],
                                      bi_mean=2, bi_stdev=1):
    """
    This generates data according to the discrete uniform distribution
    """
    xc = np.random.randint(min_val, max_val, size=(num_control, num_cov))
    xt = np.random.randint(min_val, max_val, size=(num_treated, num_cov))
            
    yc = np.dot(xc, np.array(covar_importance)) # y for control group 
    
    treatment_eff_coef = np.random.normal(bi_mean, bi_stdev, size=num_cov) # this is beta
    treatment_effect = np.dot(xt, treatment_eff_coef) # this is beta*x
        
    #second = construct_sec_order(xt[:,:2])           
    #treatment_eff_sec = np.sum(second, axis=1) # this is the last term, x_i*x_gamma
    
    # note that yc is just the 1st term of the below summation. Thus, the CATT is the 2nd term
    yt = np.dot(xt, np.array(covar_importance)) + treatment_effect #+ treatment_eff_sec
    true_catt = treatment_effect #+ treatment_eff_sec
    
    df1 = pd.DataFrame(xc, columns = range(num_cov))
    df1['outcome'] = yc
    df1['treated'] = 0
    
    df2 = pd.DataFrame(xt, columns = range(num_cov)) 
    df2['outcome'] = yt
    df2['treated'] = 1
    df = pd.concat([df2,df1])

    df = df.reset_index()
    df = df.drop(['index'], axis=1)

    return df, true_catt

def generate_binomial_given_importance(num_control=1000, num_treated=1000, 
                                   num_cov=5, bernoulli_param=0.5, 
                                   bi_mean=2, bi_stdev=1, 
                                   covar_importance=[4,3,2,1,0.01]):
    '''
    This function generates data where the covariates exponentially decay with
    importance. The x's are all binary. 
    '''
    xc = np.random.binomial(1, bernoulli_param, size=(num_control, num_cov)) # data for control group
    xt = np.random.binomial(1, bernoulli_param, size=(num_treated, num_cov)) # data for treated group
            
    yc = np.dot(xc, np.array(covar_importance)) # y for control group 
    
    treatment_eff_coef = np.random.normal(bi_mean, bi_stdev, size=num_cov) # this is beta
    treatment_effect = np.dot(xt, treatment_eff_coef) # this is beta*x
        
    #second = construct_sec_order(xt[:,:2])           
    #treatment_eff_sec = np.sum(second, axis=1) # this is the last term, x_i*x_gamma
    
    # note that yc is just the 1st term of the below summation. Thus, the CATT is the 2nd term
    yt = np.dot(xt, np.array(covar_importance)) + treatment_effect #+ treatment_eff_sec
    true_catt = treatment_effect #+ treatment_eff_sec
    
    df1 = pd.DataFrame(xc, columns = range(num_cov))
    df1['outcome'] = yc
    df1['treated'] = 0
    
    df2 = pd.DataFrame(xt, columns = range(num_cov)) 
    df2['outcome'] = yt
    df2['treated'] = 1
    df = pd.concat([df2,df1])

    df = df.reset_index()
    df = df.drop(['index'], axis=1)

    return df, true_catt


def generate_binomial_decay_importance(num_control=1000, num_treated=1000, 
                                   num_cov=5, bernoulli_param=0.5, 
                                   bi_mean=2, bi_stdev=1):
    '''
    This function generates data where the covariates exponentially decay with
    importance. The x's are all binary. 
    '''
    xc = np.random.binomial(1, bernoulli_param, size=(num_control, num_cov)) # data for control group
    xt = np.random.binomial(1, bernoulli_param, size=(num_treated, num_cov)) # data for treated group
        
    dense_bs = [ 64*((1/4)**(i+1)) for i in range(num_cov) ] 
    
    yc = np.dot(xc, np.array(dense_bs)) # y for control group 
    
    treatment_eff_coef = np.random.normal(bi_mean, bi_stdev, size=num_cov) # this is beta
    treatment_effect = np.dot(xt, treatment_eff_coef) # this is beta*x
        
    #second = construct_sec_order(xt[:,:2])           
    #treatment_eff_sec = np.sum(second, axis=1) # this is the last term, x_i*x_gamma
    
    # note that yc is just the 1st term of the below summation. Thus, the CATT is the 2nd term
    yt = np.dot(xt, np.array(dense_bs)) + treatment_effect #+ treatment_eff_sec
    true_catt = treatment_effect #+ treatment_eff_sec
    
    df1 = pd.DataFrame(xc, columns = range(num_cov))
    df1['outcome'] = yc
    df1['treated'] = 0
    
    df2 = pd.DataFrame(xt, columns = range(num_cov)) 
    df2['outcome'] = yt
    df2['treated'] = 1
    df = pd.concat([df2,df1])

    df = df.reset_index()
    df = df.drop(['index'], axis=1)

    return df, true_catt
    