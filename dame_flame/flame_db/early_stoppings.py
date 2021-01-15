



def early_stop_check0(cur,db_name,treatment_column_name,verbose):
    cur.execute('''select count(*) from {0} where is_matched=0 and {1}=0'''.format(db_name,treatment_column_name))
    if cur.fetchall()[0][0] == 0:
        if verbose:
            print("Early stopping: All control units matched")
        return True
    cur.execute('''select count(*) from {0} where is_matched=0 and {1}=1'''.format(db_name,treatment_column_name))
    if cur.fetchall()[0][0] == 0:
        if verbose:
            print("Early stopping: All treated units matched")
        return True
    return False

    
    
def early_stop_check1(baseline_PE,PE,early_stop_pe_frac,early_stop_pe,level,early_stop_iterations,
                     un_c_frac, early_stop_un_c_frac,un_t_frac, early_stop_un_t_frac,verbose): 
    
    if PE < (1.0 + early_stop_pe_frac)*baseline_PE:
        if verbose:
            print('Early stopping: predictive error would have risen ',100 * early_stop_pe_frac, '% above the baseline.')
        return True
    if PE < -early_stop_pe:
        if verbose:
            print('Early stopping: predictive error would have risen above ', early_stop_pe)
        return True
    if level > early_stop_iterations:
        if verbose:
            print('Early stopping: completed ', level-1, ' iterations and stop at level', level-1)
        return True
    if un_c_frac < early_stop_un_c_frac:
        if verbose:
            print( 'Early stopping: proportion of control units that are unmatched would have dropped below ',early_stop_un_c_frac)
        return True
    if un_t_frac < early_stop_un_t_frac:
        if verbose:
            print( 'Early stopping: proportion of treatment units that are unmatched would have dropped below ',early_stop_un_t_frac)
        return True
    
    return False