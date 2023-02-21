"""Replication file for code in dame-flame package paper.

This file contains the code to replicate the code and results in the paper
dame-flame: A Python Library Providing Fast Interpretable Matching for Causal 
Inference. Section 3.1 contains a small toy experiment, and 3.2 provides a 
real dataset.
"""
import dame_flame
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import heapq
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.preprocessing import LabelBinarizer
from statsmodels.distributions.empirical_distribution import ECDF

def replication_1():
    """ Code to replicate Section 3.1 of dame-flame paper"""
    
    df = pd.DataFrame([[0,1,1,1,0,5.1], [0,0,1,0,0,5.11], [1,0,1,1,1,6.5], 
                       [1,1,1,1,1,6.]],
                      columns=["x1", "x2", "x3", "x4", "treated", "outcome"])
    
    print(df.head())
    
    model = dame_flame.matching.DAME(verbose=3, early_stop_iterations=float('inf'))
    model.fit(df, "treated", "outcome")
    result = model.predict(df)
    
    print(result)
    print(model.units_per_group)
    
    mmg = dame_flame.utils.post_processing.MG(matching_object=model, unit_ids=0)
    print(mmg)
    
    cate = dame_flame.utils.post_processing.CATE(matching_object=model, unit_ids=0)
    print(round(cate,3))
    
    ate = dame_flame.utils.post_processing.ATE(matching_object=model)
    print(round(ate,3))
    
    #ate, var = dame_flame.utils.post_processing.var_ATE(matching_object=model)
    #print(round(ate,3))
    #print(round(var,3))
    
def replication_2():
    """Code to replicate Section 3.2 of dame-flame paper.
    
    Note that this relies on the file Star_Students.sav. To download this file,
    please see the original data on the Harvard Dataverse at this link:
    https://dataverse.harvard.edu/dataset.xhtml?persistentId=hdl:1902.1/10766
    
    Prints Figure 2 from dame-flame paper to a file with name cate-graph4.png
    
    """
    
    STAR_Students = pd.read_spss('STAR_Students.sav')
    
    df_trunc = STAR_Students.loc[:, STAR_Students.columns.intersection(
    ['gkclasstype', 'gender', 'race', 'gkfreelunch', 'gkschid', 'gktmathss', 'gktreadss', 'g1freelunch', 'g2freelunch', 'g3freelunch',
    'gktgen', 'gktrace', 'gkthighdegree', 'birthmonth', 'birthyear', 'gksurban'])]
    
    d = {"WHITE": 1, "BLACK": 0, "ASIAN": 1, "HISPANIC": 0, "OTHER": 0, 
         "NATIVE AMERICAN": 0}
    df_trunc['race'] = df_trunc['race'].map(d)
    
    d = {"NON-FREE LUNCH": 0, "FREE LUNCH": 1}
    df_trunc['gkfreelunch'] = df_trunc['gkfreelunch'].map(d)
    df_trunc['g1freelunch'] = df_trunc['g1freelunch'].map(d)
    df_trunc['g2freelunch'] = df_trunc['g2freelunch'].map(d)
    df_trunc['g3freelunch'] = df_trunc['g3freelunch'].map(d)
    
    d = {"BACHELORS": 0, "MASTERS": 1, "MASTERS + ": 1, "SPECIALIST": 1}
    df_trunc['gkthighdegree'] = df_trunc['gkthighdegree'].map(d)
    
    d = {"MALE": 1, "FEMALE": 0}
    df_trunc['gender'] = df_trunc['gender'].map(d)
    df_trunc['gktgen'] = df_trunc['gktgen'].map(d)
    
    d = {"WHITE": 1, "BLACK": 0}
    df_trunc['gktrace'] = df_trunc['gktrace'].map(d)
    
    d = {"JANUARY": 0, "FEBRUARY": 1, "MARCH": 2, "APRIL": 3, "MAY": 4, 
         "JUNE": 5, "JULY": 6, "AUGUST": 7, "SEPTEMBER": 8, "OCTOBER": 9, 
         "NOVEMBER": 10, "DECEMBER": 11}
    df_trunc['birthmonth'] = df_trunc['birthmonth'].map(d)
    
    d = {1977: 0, 1978: 1, 1979: 2, 1980:3, 1981:4}
    df_trunc['birthyear'] = df_trunc['birthyear'].map(d)
    
    d = {"RURAL": 0, "URBAN":1, "SUBURBAN": 2, "INNER CITY": 3}
    df_trunc['gksurban'] = df_trunc['gksurban'].map(d)
    
    d = {"SMALL CLASS": int(1), "REGULAR CLASS": int(0), 
         "REGULAR + AIDE CLASS": int(0)}
    df_trunc['ksmall'] = df_trunc['gkclasstype'].map(d)
    
    # Create age variable counting months
    df_trunc['age'] = df_trunc['birthyear']*12 + df_trunc['birthmonth']
    # Bin age into deciles
    df_trunc['age'] = pd.qcut(df_trunc['age'], q=10, labels=False)
    df_trunc = df_trunc.drop(columns=['gkclasstype', 'birthmonth', 'birthyear'])
    df_trunc = df_trunc.rename(columns={"ksmall": "treated"}) 

    # Fix up the free lunch variable
    for i in df_trunc.index:
        if df_trunc.loc[i, 'g1freelunch'] == 1 or df_trunc.loc[i, 'g2freelunch'] == 1 or df_trunc.loc[i, 'g3freelunch'] == 1 or df_trunc.loc[i, 'gkfreelunch'] == 1:
            df_trunc.loc[i, 'gkfreelunch'] = 1
        else:
            df_trunc.loc[i, 'gkfreelunch'] = 0
    df_trunc = df_trunc.drop(columns=['g1freelunch', 'g2freelunch', 'g3freelunch'])
    
    df_trunc = df_trunc.dropna()
    
    # Create a percentile binned outcome variable
    ecdf_reading = ECDF(df_trunc[df_trunc['treated'] == 0]['gktreadss'])
    ecdf_math = ECDF(df_trunc[df_trunc['treated'] == 0]['gktmathss'])
    df_trunc['read_outcome'] = ecdf_reading(df_trunc['gktreadss'])*100
    df_trunc['math_outcome'] = ecdf_math(df_trunc['gktmathss'])*100
    df_trunc['outcome'] = (df_trunc['read_outcome'] + df_trunc['math_outcome'])/2
    
    df_pre_drop = df_trunc
    
    # dame-flame using the percentile outcome variable
    df_trunc = df_trunc.drop(columns=['gktreadss', 'gktmathss', 'read_outcome', 'math_outcome'])
    
    # Do the matching

    '''
    models = []
    random_seeds = [1111, 2222, 3333, 4444]
    for i in range(4):
        matching_df, holdout_df = train_test_split(df_trunc, test_size=0.2, random_state=random_seeds[i])
        model_dame = dame_flame.matching.DAME(
            repeats=False, verbose=0, adaptive_weights='decisiontree')
        model_dame.fit(holdout_data=holdout_df)
        model_dame.predict(matching_df)
        models.append(model_dame)
    
    print("THE OTHER OUTCOME")
    
    for i in range(len(models)):
        ate = dame_flame.utils.post_processing.ATE(matching_object=models[i])
        print("ATE of trial", i, ":", ate,". Variance: ")
    '''
    # Same analysis on dame-flame, using the kindergarten reading scores outcome
    df_trunc = df_pre_drop.drop(columns=['outcome', 'gktmathss', 'read_outcome', 'math_outcome'])
    
    # Do the matching

    models = []
    random_seeds = [1111] #, 2222, 3333, 4444]
    for i in range(len(random_seeds)):
        matching_df, holdout_df = train_test_split(df_trunc, test_size=0.2, random_state=random_seeds[i])
        model_dame = dame_flame.matching.DAME(
            repeats=False, verbose=3, adaptive_weights='decisiontree', early_stop_pe=0.25)
        model_dame.fit(holdout_data=holdout_df, outcome_column_name='gktreadss')
        model_dame.predict(matching_df)
        models.append(model_dame)
        
    ates = []
    for i in range(len(models)):
        ate = dame_flame.utils.post_processing.ATE(matching_object=models[i])
        print("ATE of trial", i, ":", ate,". Variance: ")
        ates.append(ate)

    '''
    # compute stuff for plot
    match_dfs = []
    for i in models:
        match_dfs.append(i.input_data)
    
    for i in range(4):
        colname = 'cates'
        match_dfs[i][colname] = dame_flame.utils.post_processing.CATE(
            models[i], match_dfs[i].index)
    
    dame_len_groups = []
    dame_cate_of_groups = []
    
    for i in range(4):
    
        model_dame = models[i]
        groups = list(range(len(model_dame.units_per_group)))
    
        dame_cate_of_group = []
        dame_len_group = []
        dame_len_treated = []
        maxcate = 0.0
        maxgroupnum = 0
        index = 0
    
        flame_cate_of_group = []
        flame_len_group = []
        large_groups = []
        for group in model_dame.units_per_group:
            dame_cate_of_group.append(dame_flame.utils.post_processing.CATE(
                model_dame, group[0]))
            dame_len_group.append(len(group))
    
            # find len of just treated units
            df_mmg = df_trunc.loc[group]
            treated = df_mmg.loc[df_mmg["treated"] == 1]
    
        dame_len_groups.append(dame_len_group)
        dame_cate_of_groups.append(dame_cate_of_group)
        
    # Create the plot, Figure 2 in the paper

    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize = (19,13), 
                                                 sharex=True, sharey=True)
    fig.text(0.5, 0.05, 'Number of Units in Matched Group', ha='center', 
             fontsize=26)
    fig.text(0.05, 0.5, 'Log Transformed Treatment Effect of Matched Group', 
             va='center', rotation='vertical', fontsize=26)
    fig.suptitle("CATE Estimates from DAME for Four Random Samples from STAR Dataset", fontsize=28, y=0.91)
    ax1.axhline(y=np.log10(ates[0]), color='r', linestyle='-')
    ax2.axhline(y=np.log10(ates[1]), color='r', linestyle='-')
    ax3.axhline(y=np.log10(ates[2]), color='r', linestyle='-')
    ax4.axhline(y=np.log10(ates[3]), color='r', linestyle='-')
    
    ax1.tick_params(labelsize=26)
    ax2.tick_params(labelsize=26)
    ax3.tick_params(labelsize=26)
    ax4.tick_params(labelsize=26)
    
    al=0.2
    
    temp = np.array(dame_cate_of_groups[0])
    result = np.log10(temp, where=temp>0, out=temp)
    result = -1*np.log10(result*-1, where=result<0,out=result*-1)
    ax1.scatter(dame_len_groups[0], result, color="purple", 
                alpha = al)
    ax1.text(0.8, 0.9,'ATE: '+str(round(ates[0],2)), ha='center', va='center',
             transform=ax1.transAxes, fontsize=26)
    
    temp = np.array(dame_cate_of_groups[1])
    result = np.log10(temp, where=temp>0, out=temp)
    result = -1*np.log10(result*-1, where=result<0,out=result*-1)
    ax2.scatter(dame_len_groups[1], result, color="green", 
                alpha = al)
    ax2.text(0.8, 0.9,'ATE: '+str(round(ates[1],2)), ha='center', va='center',
             transform=ax2.transAxes, fontsize=26)
    
    temp = np.array(dame_cate_of_groups[2])
    result = np.log10(temp, where=temp>0, out=temp)
    result = -1*np.log10(result*-1, where=result<0,out=result*-1)
    ax3.scatter(dame_len_groups[2], result, color="blue", 
                alpha = al)
    ax3.text(0.8, 0.9,'ATE: '+str(round(ates[2],2)), ha='center', va='center',
             transform=ax3.transAxes, fontsize=26)
    
    temp = np.array(dame_cate_of_groups[3])
    result = np.log10(temp, where=temp>0, out=temp)
    result = -1*np.log10(result*-1, where=result<0,out=result*-1)
    ax4.scatter(dame_len_groups[3], result, color="magenta",
                alpha = al)
    ax4.text(0.8, 0.9,'ATE: '+str(round(ates[3],2)), ha='center', va='center',
             transform=ax4.transAxes, fontsize=26)
    
    plt.subplots_adjust(wspace=.02, hspace=.02)
    plt.savefig('cate-graph4-replicationnnn.png', dpi = 200)
    '''
    ## FLAME on the outcome instead.
    ## This is the information that goes into Table 2 of the paper.
    flame_models = []
    random_seeds = [1111] #, 2222, 3333, 4444]
    for i in range(len(random_seeds)):
        matching_df, holdout_df = train_test_split(df_trunc, test_size=0.2, random_state=random_seeds[i])
        model_flame = dame_flame.matching.FLAME(
            repeats=False, verbose=3, adaptive_weights='decisiontree', 
            missing_holdout_replace=1, missing_data_replace=1, 
            early_stop_pe=True)
        model_flame.fit(holdout_data=holdout_df, outcome_column_name='gktreadss')
        result_flame = model_flame.predict(matching_df)
        flame_models.append(model_flame)
    