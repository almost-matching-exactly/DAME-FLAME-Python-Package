from flame_db.matching_helpers import *
from flame_db.checker import *
from flame_db.early_stoppings import *

#This function is to print each iteration of dropping and matching. 
def print_process(PE,BF,level,matching_option,is_unimportant,fixed_weights,cov_to_drop,cur_covs,verbose):
    if verbose == 2 or verbose == 3:
        string = "Level"+ str(level)
        if matching_option == 0 and is_unimportant:
            string += ": No matching after "
        else:
            string += ": Do matching after "

        if matching_option == 2 or fixed_weights or is_unimportant: 
            string += "fast drop "
        else:
            string += "slow drop "

        string += cov_to_drop + " with "
        if matching_option == 2 or fixed_weights:
            string += "fixed "
        else:
            string += "adaptive "
        string += "score: (PE: " +str(-PE) + " BF: " + str(BF) + ')'
        print(string)
        
#This function is to print statistics after each iteration.         
def print_stats(total_control, total_treated, un_matched_control, un_matched_treated,ds, level_matched, level, verbose):
    matched_control = int(total_control - un_matched_control)
    matched_treated = int(total_treated - un_matched_treated)
    num_matched_groups = 0
    num_units_matched_this_level = 0
    for d_ in ds:
        num_matched_groups += d_.shape[0]
        
    if verbose == 3:
        print("\tNumber of units matched so far: ", matched_control+matched_treated)
        print("\tNumber of covariates dropped in total: ", level - 1)
        print("\tNumber of matched groups formed in total: ", num_matched_groups)
        print("\tUnmatched treated units: ", 
              int(un_matched_treated), "out of a total of ",total_treated, "treated units")
        print("\tUnmatched control units: ", 
              int(un_matched_control), "out of a total of ",total_control, "control units")




# Main function
def run_main(db_name, holdout_df,treatment_column_name,outcome_column_name, 
             cur, conn, tradeoff, k, ratio,adaptive_weights,alpha, 
             max_depth,random_state,weight_array,matching_option,verbose, 
             early_stop_iterations, early_stop_un_c_frac,early_stop_un_t_frac,
             early_stop_pe_frac,early_stop_pe
            ):
    
    #Add column "matched" to dataset
    
    cur.execute('''ALTER TABLE {0} DROP COLUMN IF EXISTS is_matched;'''.format(db_name)) # reset the matched indicator to 0
    conn.commit()
    cur.execute('''ALTER TABLE {0} ADD COLUMN is_matched Integer;
                   update {0} set is_matched = 0'''.format(db_name)) # reset the matched indicator to 0
    conn.commit()
    covs_dropped = [] # covariate dropped
    ds = []
    level_matched = [] # To store levels where we do matching
    level = 1
    cur_covs = holdout_df.columns.drop([treatment_column_name, outcome_column_name])
    fixed_weights = True if adaptive_weights==False else False
    is_unimportant = True # Flag to decide if we just drop without matching
    flag_switch_bounday = False #  True if we find the point where we start to switch from fast to slow drop
    
    #Get total treated and control units  in the database
    cur.execute('''select count(*) from {0} where is_matched=0 and {1}=0'''.format(db_name,treatment_column_name))
    total_control = cur.fetchall()[0][0]
    cur.execute('''select count(*) from {0} where is_matched=0 and {1}=1'''.format(db_name,treatment_column_name))
    total_treated =  cur.fetchall()[0][0]
    un_matched_control = total_control
    un_matched_treated = total_treated
    
 
    #Map all covs of holdout set into dummy variables
    df_dummy,mapp_,curr_dummy = do_mapping(holdout_df, treatment_column_name, outcome_column_name)
    
 
    # do varible importance selection to get the dictionary of covs weights 
    (sorted_covs,cur_covs) = compute_weights(df_dummy, mapp_, curr_dummy,fixed_weights, weight_array, cur_covs,
                                             holdout_df,treatment_column_name,outcome_column_name,
                                             adaptive_weights,alpha,max_depth,random_state)
    
    
    #Get the baseline of PE when we do not drop any covariate
    baseline_PE = 0
    if not fixed_weights:
        baseline_PE = get_PE_db(df_dummy, mapp_, curr_dummy,cur_covs.keys(),None,holdout_df,treatment_column_name,
                            outcome_column_name, adaptive_weights,alpha,max_depth,random_state)
    

    
    #Matching without drop any covs                
    res = do_matched_covs(ds,level_matched,cur_covs.keys(),
                          un_matched_control,un_matched_treated,db_name,k,
                          level,cur,conn,treatment_column_name,outcome_column_name)
    (ds,level_matched,un_matched_control,un_matched_treated) = res 
    if verbose==2 or verbose ==3:
        print("Level"+ str(level) +": Do matching without dropping any covs")
    
    
    #Start to drop covariate
    while len(cur_covs)>1:
        level += 1
        
        PE = 0 #To store the PE of cov to be dropped in this level
        BF = 0 #To store the BF of cov to be dropped in this level
        best_score = -np.inf #To store the score (C*BF+PE) of cov to be dropped in this level
        cov_to_drop = None #To store the covarite to be dropped in this level
        

        # the early stopping conditions
        if early_stop_check0(cur,db_name,treatment_column_name,verbose):
            break
        
        
        if matching_option == 2 or fixed_weights:
            #Fast drop every covaraite with fixed scores from the function compute_weights
            #Need to consider two cases: 1. tradeoff = 0; 2. tradeoff != 0
            if tradeoff != 0:
                for c, PE_ in cur_covs.items():
                    BF_ = get_BF_db(cur_covs.keys(),c,k,cur,db_name,treatment_column_name,outcome_column_name)
                    score = tradeoff * BF_ + PE_
                    if score > best_score:
                        PE,BF,best_score,cov_to_drop = PE_,BF_,score, c
            else:
                cov_to_drop, PE = sorted_covs[level-2][0],sorted_covs[level-2][1]
                BF = get_BF_db(cur_covs.keys(),cov_to_drop,k,cur,db_name,treatment_column_name,outcome_column_name)


        else:
            #if matching_option ==3, we carefully drop each cov. This is the original method in FALME paper
            #In other words, we will treat every cov as important if matching_option ==3.
            if matching_option == 3:
                is_unimportant = False
                
            # The general idea of below code  
            # Fast drop unimportant covaraite with fixed score and slow drop important covatraites with adaptive socres
            #    Case1: If the cov is unimportant, just fast drop the cov based on fixed score
            #    Case2: If the cov is important, slow drop the cov with smallest abosolute PE by cross-validation

            #Start on fast dropping unimportant covs
            if is_unimportant:
                #A cov is unimportant if both of its fixed and adaptive score >= bound.   
                #This part is only to decide if a cov is important or not
                if  max(cur_covs.values()) >= (1 + ratio)*baseline_PE: #Rule1: is unimportant if fixed score >= bound
                    c = sorted_covs[level-2][0]
                    cov_to_drop = c
                    PE = get_PE_db(df_dummy, mapp_, curr_dummy,cur_covs.keys(),c,holdout_df,treatment_column_name,
                            outcome_column_name, adaptive_weights,alpha,max_depth,random_state)
                    BF = get_BF_db(cur_covs.keys(),c,k,cur,db_name,treatment_column_name,outcome_column_name)
                    
                    if PE < (1 + ratio)*baseline_PE: #Rule2: is important if adaptive score < bound
                        is_unimportant,flag_switch_bounday = False,True

                else:
                    is_unimportant,flag_switch_bounday = False,True


            #Find the switch boundary from fast drop to slow drop
            #We need this because we need do matching after drop all unimportant covs and before drop important one
            #Only need this if matching_option == 0
            if not is_unimportant and flag_switch_bounday and matching_option == 0: 
                flag_switch_bounday = False
                res = do_matched_covs(ds,level_matched,cur_covs.keys(),un_matched_control,un_matched_treated,
                                      db_name,k,level-1,cur,conn,treatment_column_name,outcome_column_name)
                (ds,level_matched,un_matched_control,un_matched_treated) = res
                if  verbose == 2 or verbose ==3:
                    print("Found the boundary to switch to slowly dropping important covariates.")
            
            # Switch to slow drop and search the best covariate to drop
            if not is_unimportant:
                for c, _ in cur_covs.items():
                    PE_ = get_PE_db(df_dummy, mapp_, curr_dummy,cur_covs.keys(),
                                    c,holdout_df,treatment_column_name, outcome_column_name,
                              adaptive_weights,alpha,max_depth,random_state)
                    BF_ = get_BF_db(cur_covs.keys(),c,k,cur,db_name,treatment_column_name,outcome_column_name)
                    score = tradeoff * BF_ + PE_
                    if score > best_score:
                        PE,BF,best_score,cov_to_drop = PE_,BF_,score, c
                        

                    
        # the early stopping conditions            
        if early_stop_check1(baseline_PE,PE,early_stop_pe_frac,early_stop_pe,level,early_stop_iterations,
                                   un_matched_control/total_control, early_stop_un_c_frac,un_matched_treated/total_treated, 
                                   early_stop_un_t_frac,verbose):
            break 
         
        #Print info
        print_process(PE,BF,level,matching_option,is_unimportant,fixed_weights,cov_to_drop,cur_covs,verbose)       
        print_stats(total_control, total_treated, un_matched_control, un_matched_treated,ds,level_matched, level, verbose)
        del cur_covs[cov_to_drop]
        curr_dummy = set(curr_dummy) -  mapp_[cov_to_drop]
        
        # If the cov is unimpoartant and matching_option == 0, just drop it without matching
        if matching_option == 0 and is_unimportant and (not fixed_weights):
            continue  
        
        #Update the database and matched groups and other statistics like CATE
        res = do_matched_covs(ds,level_matched,cur_covs.keys(),un_matched_control,un_matched_treated,db_name,k,
                              level,cur,conn,treatment_column_name,outcome_column_name)
        (ds,level_matched,un_matched_control,un_matched_treated) = res
        covs_dropped.append(cov_to_drop) # append the removed covariate at the end of the covariate
    
    if verbose:
        print("Done matching:")
        print_stats(total_control, total_treated, un_matched_control, un_matched_treated,ds,level_matched, level, verbose = 3)
    return ds,level_matched,covs_dropped



def FLAME_db(input_data, holdout_data,conn, treatment_column_name = "treated", outcome_column_name ="outcome",
             weight_array=[],adaptive_weights = 'decisiontree',alpha = 0.1,max_depth = 8,random_state = None,
             early_stop_iterations = np.inf, early_stop_un_c_frac = 0, early_stop_un_t_frac = 0,
             early_stop_pe_frac = 0.25,early_stop_pe = np.inf, 
             C = 0,k = 2, ratio = 0.01, matching_option = 0,verbose = 1,
             missing_data_replace = 0, missing_holdout_replace = 0
            ):
    """
    Args:
        input_data(string, required parameter):
            the name of your table in the database that contains the dataset to be matched
        holdout_data (string, dataframe,required parameter):
            This is the holdout dataset. If a string is given, that should be 
            the location of a CSV file to input. 
        conn (object, required parameter):
            This is the output from database connector
        treatment_column_name(string, default="treated"): 
            the name of the column with a binary indicator for whether a row is
            a treatment or control unit.
        outcome_column_name (string, default="outcome"): 
            This is the name of the column with the outcome variable of each 
            unit.
        weight_array (array, defualt=None):
            If adaptive_weights = False, these are the weights to the 
            covariates in input_data. Must sum to 1. In this case, we do not use machine
            learning for the weights, they are manually entered as weight_array.
        adaptive_weights (bool, str, default='decisiontree'): 
            Weight dropping method. False, 'ridge', or 'decisiontree'. 
        alpha (float, default=0.1): 
            This is the alpha for ridge regression. We use the 
            scikit package for ridge regression, so it is "regularization 
            strength". Larger values specify stronger regularization. 
            Must be positive float. 
        max_depth (integer, default=8): 
            This is the max_depth for decision tree. We use the 
            scikit package for decision tree, must be positive integer. 
        random_state (int or RandomState instance, default=None): 
            random_state for machine learning algorithm you are using
        early_stop_iterations (int, defualt=np.inf): 
            If provided, a number of iters to hard stop the algorithm after this.
        early_stop_un_c_frac (optional float, from 0.0 - 1.0, default=0.0): 
            If provided, a fraction of unmatched control treatment 
            units. When threshold met, hard stop the algo.        
        early_stop_un_t_frac (optional float, from 0.0 - 1.0, default=0.0): 
            If provided, a fraction of unmatched control
            units. When threshold met, hard stop the algo.
        early_stop_pe (float, default = np.inf): 
            If FLAME attempts to drop a covariate that would lead to a PE above 
            this value, the algorithm will hard stop.
        early_stop_pe_frac(float, default = 0.25): 
            If the covariate set chosen to match on has a PE higher 
            than (1+early_stop_pe_frac)*baseline_PE, the algorithm will stop.
        C (float, default=0.1): 
            The tradeoff between PE and BF in computing MQ
        k (int, default = 2): 
            A constraint on the number of units for each matched group.
            We have matched gourp with the number of units at least k.
        ratio (float, default=0.01): 
            A hyperparameter to decide if we should do fast dropping unimportant covariates 
            without matching. We only treat a covariate i unimportant if PE_i1 > (1+ratio)*baseline_PE 
            and  PE_i2 > (1+ratio)*baseline_PE. PE_i1 is the fiexed predicted error on whole 
            holdout without covariate i, computed at the very beginning and PE_i2 
            is adaptive predicted error on current remaining holdout without covariate i. 
        matching_option (0,1,2, default=0):
            If 0, no match after fast drop unimportant covariates and do matching 
            after slow dropping important covariates. 
            If 1, do matching after fast and slow drop.
            If 2, do matching with fixed weights or a fixed scores computed by FLAME
            If 3, do matching after slow drop each cov. (Original method in paper)
        verbose (0,1,2,3,default=2):
            If 0, no info is displayed
            if 1, only provides the statistic in the end
            If 2, provides 1 and provides level num and covariate to be dropped 
            and its score at each level. 
            If 3, provides 1 and 2 and also print other statistics. If 0, nothing. 
        missing_holdout_replace (0,1, default=0):
            if 0, assume no missing holdout data and proceed
            if 1, drop all missing_indicator values from holdout dataset
        missing_data_replace (0,1,2, default=0):
            if 0, assume no missing data in matching data and proceed
            if 1, drop all missing_indicator values from matching data
            if 2, will not match a unit on a covariate that it is missing
        
    Returns:
        res[0]:
            df of units with the column values of their main matched
            group. Each row represent one matched groups.
            res[0]['avg_outcome_control']: 
                average of control units' outcomes in each matched group   
            res[0]['avg_outcome_treated']: 
                average of treated units' outcomes in each matched group   
            res[0]['num_control']:
                the number of control units in each matched group
            res[0]['num_treated']:
                the number of treated units in each matched group
            res[0]['is_matched']:
                the level each matched group belongs to
        res[1]:
            a list of level numbers where we have matched groups
        res[2]:
            a list of covariate names that we dropped
                
    """


    cur = conn.cursor()
    
    #Read file
    holdout_data = read_files(input_data, holdout_data)
    # Check if  input in the database and holdout have legal data type
    check_parameters(holdout_data,adaptive_weights,weight_array,C, k, ratio, matching_option,verbose,alpha, max_depth,
                         random_state, missing_data_replace, missing_holdout_replace) 
    check_stops(early_stop_un_c_frac, early_stop_un_t_frac, early_stop_pe, early_stop_pe_frac)
    check_missings(input_data, holdout_data, conn, missing_data_replace, 
               missing_holdout_replace, treatment_column_name, outcome_column_name) 

    check_holdout_file(holdout_data, treatment_column_name, outcome_column_name)
    check_input_file(input_data, cur, conn, treatment_column_name, outcome_column_name)

   



    #Do macthing
    res = run_main(input_data, holdout_data,treatment_column_name,outcome_column_name, 
                   cur, conn, C, k, ratio,adaptive_weights,alpha, 
                   max_depth,random_state,weight_array, matching_option,verbose,
                   early_stop_iterations, early_stop_un_c_frac, early_stop_un_t_frac,
                   early_stop_pe_frac,early_stop_pe 
                  )
    
    return res


