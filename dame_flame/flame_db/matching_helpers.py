import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import cross_val_score

#This function is to map all covs of dataset into dummy variables
def do_mapping(df,treatment_column_name,outcome_column_name):
    covs = df.columns.drop([treatment_column_name,outcome_column_name])
    df_ = df[covs].copy().astype(str)
    mapp_ = dict()
    for col in df_.columns:
        set_ = set()
        for i in pd.unique(df_[col]):
            set_.add(col + '_'  + i)
        mapp_[col] = set_
    df_dummy = pd.get_dummies(df_.astype(str))
    curr_dummy = df_dummy.columns
    df_dummy.insert(loc=len(df_dummy.columns), column=treatment_column_name, value=df[treatment_column_name])
    df_dummy.insert(loc=len(df_dummy.columns), column=outcome_column_name, value=df[outcome_column_name])
    return  df_dummy, mapp_,curr_dummy

# This function is to compute the scores for each covariate at the very beginning.
def compute_weights(df_dummy, mapp_, curr_dummy,fixed_weights, weight_array, cur_covs, holdout_df,
                    treatment_column_name,outcome_column_name,adaptive_weights,alpha,max_depth,random_state):

    order_cov = dict()
    for i in range(len(cur_covs)):
        c = cur_covs[i]
        if fixed_weights == False:
            order_cov[c] = get_PE_db(df_dummy, mapp_, curr_dummy,cur_covs,c,holdout_df,
                                     treatment_column_name, outcome_column_name,
                                      adaptive_weights,alpha,max_depth,random_state)
            
        else:
            order_cov[c] = -weight_array[i] #convert into negative socre, we are tring to drop the biggest score
    
    sorted_covs = sorted(order_cov.items(), key=lambda item: item[1],reverse = True) # sorted weight
    cur_covs = dict(sorted_covs)
    
    return (sorted_covs,cur_covs)


# This function is to update the "matched" column in database for all units matched in this level.
# Then get all stastics for each matched group: the number of control and treated units
# average outcome for control and treated units
def do_matched_covs(ds,level_matched, cov_l,un_matched_control,un_matched_treated,
                    db_name,k, level,cur, conn,treatment_column_name,outcome_column_name):
    
    #Update the "matched" column of the newly mathced units to be "level"
    cur.execute('''with temp AS 
    (SELECT 
    {0}
    FROM {3}
    where is_matched=0
    group by {0}
    Having sum({5})>0 and sum({5})<count(*)  and count(*) >= {7}
    )
    update {3} set is_matched={4}
    WHERE EXISTS
    (SELECT {0}
    FROM temp
    WHERE {2} and {3}.is_matched = 0
    )
    '''.format(','.join(['{0}'.format(v) for v in cov_l]),
               ','.join(['{1}.{0}'.format(v, db_name) for v in cov_l]),
               ' AND '.join([ '{1}.{0}=temp.{0}'.format(v, db_name) for v in cov_l ]),
               db_name,
               level,
               treatment_column_name,
               outcome_column_name,
               k
              ) )
    conn.commit()

    # For this level, get the matched covariates, average outcome for control and treated units respectively,
    # the number of control and treated units respectively for each matched groups
    # Combine these above as result_df. Each row of result_df is a matched group
    cur.execute(''' select {0}, avg({4} * 1.0), count(*)
                    from {1}
                    where is_matched = {2} and {3} = 0
                    group by {0}
                    '''.format(','.join(['{0}'.format(v) for v in cov_l]), 
                              db_name, level, treatment_column_name,outcome_column_name) )
    res_c = cur.fetchall()
    
    cur.execute(''' select {0}, avg({4} * 1.0), count(*)
                    from {1}
                    where is_matched = {2} and {3} = 1
                    group by {0}
                    '''.format(','.join(['{0}'.format(v) for v in cov_l]), 
                              db_name, level, treatment_column_name,outcome_column_name) )
    res_t = cur.fetchall()

    #Make sure that a matched group have both control and treated units
    if  (len(res_c) != 0) and (len(res_t) != 0):
        cov_l = list(cov_l)
        result = pd.merge(
            pd.DataFrame(np.array(res_c), columns=['{}'.format(i) for i in cov_l]+['avg_outcome_control', 'num_control']), 
            pd.DataFrame(np.array(res_t), columns=['{}'.format(i) for i in cov_l]+['avg_outcome_treated', 'num_treated']), 
            on = ['{}'.format(i) for i in cov_l], how = 'inner') 

        result_df = result[['{}'.format(i) for i in cov_l] + 
                           ['avg_outcome_control', 'avg_outcome_treated', 'num_control', 'num_treated']]
    
        result_df.insert(loc=len(result_df.columns), column='is_matched', value=level)

        result_df = result_df.astype({"num_control": int, "num_treated": int,
                                      'avg_outcome_control': np.float64, 'avg_outcome_treated':np.float64 })
                                                 
        ds.append(result_df)
#         print("*****************************************************")
#         print("before")
#         print(un_matched_control)
#         print(un_matched_treated)
#         print(result_df.loc[:,'num_control'])
#         print(result_df.loc[:,'num_treated'])
        un_matched_control -= result_df.loc[:,'num_control'].sum()
        un_matched_treated -= result_df.loc[:,'num_treated'].sum()
#         print("after")
#         print(un_matched_control)
#         print(un_matched_treated)
        level_matched.append(level)
        
        cur.execute(''' select count(*)
                        from {1}
                        where is_matched = 0
                        '''.format(','.join(['{0}'.format(v) for v in cov_l]), 
                                  db_name, level, treatment_column_name,outcome_column_name) )
        res_t = cur.fetchall()[0][0]        
        
#         print("un_matched in total: ", res_t)
#         print("matched in total: ", 5000-res_t )
        
    return (ds,level_matched,un_matched_control,un_matched_treated)

# This function is to get PE for given set of covariates
def get_PE_db(df_dummy, mapp_, curr_dummy,cov_l,c,holdout_df,treatment_column_name, outcome_column_name,
              adaptive_weights,alpha,max_depth,random_state):
    
    covs_to_match_on = set(cov_l) - {c} # the covariates to match on
    covs_to_match_on = set(curr_dummy)
    if c!=None:
         covs_to_match_on = set(curr_dummy)- mapp_[c]
    
    holdout_df = df_dummy
    
    model_c = None
    model_t = None
    
    if adaptive_weights == 'ridge':
        model_c = Ridge(fit_intercept = False, alpha= alpha, random_state=random_state)
        model_t = Ridge(fit_intercept = False, alpha= alpha, random_state=random_state)
    if adaptive_weights == 'decisiontree':
        model_c = DecisionTreeRegressor(max_depth = max_depth, random_state=random_state)
        model_t = DecisionTreeRegressor(max_depth = max_depth, random_state=random_state)

    holdout = holdout_df.copy()
    holdout = holdout[ ["{}".format(c) for c in covs_to_match_on] + [treatment_column_name, outcome_column_name]]

    mse_t = np.mean(cross_val_score(model_t, holdout[holdout[treatment_column_name] == 1].iloc[:,:-2], 
                                    holdout[holdout[treatment_column_name] == 1][outcome_column_name]  
                                     ,scoring  = 'neg_mean_squared_error') )#scoring
        
    mse_c = np.mean(cross_val_score(model_c, holdout[holdout[treatment_column_name] == 0].iloc[:,:-2], 
                                    holdout[holdout[treatment_column_name] == 0][outcome_column_name]
                                     ,scoring = 'neg_mean_squared_error') )# 
    
    PE = mse_t + mse_c
   
    return PE

# This function is to get BF for given set of covariates
def get_BF_db(cov_l,c,k,cur,db_name,treatment_column_name,outcome_column_name):
    '''
    cov_l: current covariates to be matched
    c: the covariate tend to be dropped
    db_name: the name of input data in the database
    '''
    
    BF = 0
    covs_to_match_on = set(cov_l) - {c} # the covariates to match on
    
    # the flowing query fetches the matched results (the variates, the outcome, the treatment indicator)
    cur.execute('''with temp AS 
        (SELECT 
        {0}
        FROM {3}
        where is_matched=0
        group by {0}
        Having sum({4})> 0 and sum({4})<count(*) and count(*) >= {6}
        )
        (SELECT {1}, {4}, {5}
        FROM {3}
        WHERE is_matched=0 AND EXISTS 
        (SELECT 1
        FROM temp 
        WHERE {2}
        )
        )
        '''.format(','.join(['{0}'.format(v) for v in covs_to_match_on ]),
                   ','.join(['{1}.{0}'.format(v, db_name) for v in covs_to_match_on ]),
                   ' AND '.join([ '{1}.{0}=temp.{0}'.format(v, db_name) for v in covs_to_match_on ]),
                   db_name,treatment_column_name,outcome_column_name,k) )
    res = np.array(cur.fetchall())

    # the number of unmatched treated units
    cur.execute('''select count(*) from {0} where is_matched = 0 and {1} = 0'''.format(db_name,treatment_column_name))
    num_control = cur.fetchall()
    # the number of unmatched control units
    cur.execute('''select count(*) from {0} where is_matched = 0 and {1} = 1'''.format(db_name,treatment_column_name))
    num_treated = cur.fetchall()

    
        
    if len(res) != 0:
        treatment_col = np.array(res[:,-2], dtype='int32',copy=True)
        BF = (float(len(treatment_col[treatment_col==0]))/num_control[0][0] +
              float(len(treatment_col[treatment_col==1]))/num_treated[0][0])

    return BF


