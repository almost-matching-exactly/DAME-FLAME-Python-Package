---
layout: default
title: Introduction
nav_order: 1
permalink: /documentation/api-documentation/Introduction
parent: API Documentation
grand_parent: Documentation
has_children: true
---

# API Documentation Introduction
{: .no_toc }

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## DAME and FLAME Parameters and Defaults

<div class="code-example" markdown="1">
```python
__init__(self, adaptive_weights='ridge', alpha=0.1, repeats=True,
         verbose=2, early_stop_iterations=False, 
         stop_unmatched_c=False, early_stop_un_c_frac=False, 
         stop_unmatched_t=False, early_stop_un_t_frac=False, 
         early_stop_pe=False, early_stop_pe_frac=0.01, 
         early_stop_bf=False, early_stop_bf_frac=0.01,
         missing_indicator=np.nan, missing_data_replace=0, 
         missing_holdout_replace=0, missing_holdout_imputations=10, 
         missing_data_imputations=1, want_pe=False, want_bf=False)
fit(self, holdout_data=False, treatment_column_name='treated',
          outcome_column_name='outcome', weight_array=False)     
predict(self, input_data)       
```
</div>

### Key parameters

**input_data**: file, DataFrame, required
This is the data being matched. This is henceforth referred to as the matching data. 

**treatment_column_name**: string, optional (default="treated")  
This is the name of the column with a binary indicator for whether a row is a treatment or control unit.

**outcome_column_name**: string, optional (default="outcome")  
This is the name of the column with the outcome variable of each unit. 

**adaptive_weights**: bool, "ridge", "decision tree", "ridgeCV", optional (default="ridge")  
The method used to decide what covariate set should be dropped next.

**weight_array**: array, optional  
If adaptive_weights = False, these are the weights to the covariates in **input_data**, for the non-adaptive version of DAME. Must sum to 1. In this case, we do not use machine learning for the weights, they are manually entered as **weight_array**.

**alpha**: float, optional (default=0.1)  
If adaptive_weights is set to ridge, this is the alpha for ridge regression.

**holdout_data**: file, DataFrame, float between 0 and 1, optional (Default = False)
If doing an adaptive_weights version of DAME, this is used to decide what covariates to drop. The default is to use 10% of the **input_data** dataset. Users can specify a percentage of the matching data set to use as the holdout set, or use a different file. If using a different file, that file needs to have all of the same column labels, including treatment and outcome columns.

**repeats**: Bool, optional (default=True)  
Whether or not units for whom a main matched has been found can be used again, and placed in an auxiliary matched group. 


**verbose**: int 0,1,2,3 (default=2)  
Style of printout while algorithm runs.
If 0, no output 
If 1, provides iteration number 
If 2, provides iteration number and additional information on the progress of the matching at every 10th iteration
If 3, provides iteration number and additional information on the progress of the matching at every iteration


**want_pe**: bool, optional (default=False)  
If true, the output of the algorithm will include the predictive error of the covariate sets used for matching in each iteration.


**want_bf**: bool, optional (default=False)  
If true, the output will include the balancing factor for each iteration.

#### FLAME-specific parameters

**pre_dame**: bool, integer, optional (default=False)  
This will allow a user to run the Hybrid-FLAME-DAME algorithm. If an integer n is provided, then after n iterations of FLAME, the algorithm will switch to DAME. 


**C**: float, optional (default=0.1)
This is used in deciding the best covariate match during iterations of FLAME. Specifically, its the tradeoff parameter between balancing factor and predictive error. 


### Parameters related to missing data handling

A variety of built-in options for missing data handling functionality is available to users.

The fastest option is to exclude missing values for each unit in the matching dataset, and drop missing units entirely from the holdout dataset.
The units with missing values would still be placed in a group, but the covariates for which they
have missing data wouldn't be used to find their group. Holdout missing data would
be dropped.  These are parameters missing_holdout_replace=1, missing_data_replace=2. 

If missing data is detected, but the user has not specified a handling technique, then
(does it quit?) 

**missing_indicator**: character, integer, numpy.nan, optional (default=numpy.nan)  
This is the indicator for missing data in the dataset. 

**missing_holdout_replace**: int 0,1,2, optional (default=0)  
If 0, assume no missing holdout data and proceed. 
If 1, the algorithm excludes units with missing values from the holdout dataset. 
If 2, do MICE on holdout dataset. If this option is selected, it will be done for a number of iterations equal to **missing_holdout_imputations**.

**missing_data_replace**: int 0,1,2,3, optional, (default=0)  
If 0, assume no missing data in matching data and proceed. 
If 1, the algorithm does not match on units that have missing values. 
If 2, prevent all **missing_indicator** values from being matched on. 
If 3, do MICE on matching dataset. This is not recommended. If this option is selected, it will be done for a number of iterations equal to **missing_data_imputations**.

**missing_holdout_imputations**: int, optional (default=10)  
If missing_holdout_replace=2, the number of imputations.

**missing_data_imputations**: int, optional (default=1)  
If missing_data_replace=3, the number of imputations. 


###  Parameters related to early stopping criteria


**early_stop_iterations**: int, optional  (default=0)  
If provided, a number of iterations after which to hard stop the algorithm.

**stop_unmatched_c**: bool, optional (default=False)  
If True, then the algorithm terminates when there are no more control units to match. 

**stop_unmatched_t**: bool, optional (default=False)  
If True, then the algorithm terminates when there are no more treatment units to match. 

**early_stop_un_c_frac**: float from 0.0 to 1.0, optional (default=0.1)  
This provides a fraction of unmatched control units. When the threshold is met, the algorithm will stop iterating. For example, using an input dataset with 100 control units, the algorithm will stop when 10 control units are unmatched and 90 are matched (or earlier, depending on other stopping conditions).

**early_stop_un_t_frac**: float from 0.0 to 1.0, optional (default=0.1)
This provides a fraction of unmatched treatment units. When the threshold is met, the algorithm will stop iterating. For example, using an input dataset with 100 treatment units, the algorithm will stop when 10 control units are unmatched and 90 are matched  (or earlier, depending on other stopping conditions).

**early_stop_pe**: bool, optional (default=False)  
If this is true, then if the covariate set chosen for matching has a predictive error higher than the parameter **early_stop_pe_frac**, the algorithm will stop.

**early_stop_pe_frac**: float, optional (default=0.01)  
If **early_stop_pe** is true, then if the covariate set chosen for matching has a predictive error higher than this value, the algorithm will stop.

**early_stop_bf**: bool, optional (default=False)  
If this is true, then if the covariate set chosen for matching has a balancing factor lower than early_stop_bf_frac, then the algorithm will stop.

**early_stop_bf_frac**: float, optional (default=0.01)  
If early_stop_bf is true, then if the covariate set chosen for matching has a balancing factor lower than this value, then the algorithm will stop.

## Additional Functions Available, and their parameters and defaults

To provide users with additional options in analyzing the output of DAME and FLAME, we provide a set of functions that can be used after running the match.

<div class="code-example" markdown="1">
```python
# The main matched group of a unit or list of units
MG(matching_object, unit_ids)
# The conditional average treatment effect for a unit or list of units
CATE(matching_object, unit_ids)
# The average treatment effect for the matching data
ATE(matching_object)
# The average treatment effect on the treated for the matching data
ATT(matching_object)
```
</div>

### Parameters 

**return_df**: Python Pandas Dataframe, required (no default).
This is output from `FLAME` or `DAME`

**unit_ids**: int, list, required (no default).
This is the unit or list of units for which the main matched group or treatment effect is being calculated

**input_data**: file, DataFrame, required (no default)
This is the matching data. 

**output_style**: int, optional (default=1):
In the MG function, if this is 1 then the main matched group will only display covariates that were used in matching for each unit. The output dataframe will have a ' * ' character in the column for each unit that was not matched on that covariate.
If this value is 2, then the dataframe will contain complete values and no ' * ' characters.

**treatment_column_name**: string, optional (default="treated")  
This is the name of the column with a binary indicator for whether a row is a treatment or control unit.

**outcome_column_name**: string, optional (default="outcome")  
This is the name of the column with the outcome variable of each unit. 

## Additional Technical Notes

### Missing Data Handling

For details on the MICE algorithm, see : [this paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3074241/)
The underlying MICE implementation is done using scikit learn's experimental IterativeImpute package, 
and relies on DecisionTreeRegressions in the imputation process, to ensure that the data generated
is fit for unordered categorical data. In addition to this, users are welcome to pre-process their datsets with other data handling techniques
prior to using MICE. It is not recommended to use MICE on the matching dataset, as this would be very slow.  

One option is to set the parameter missing_data_replace=2, where units that have missing values are still matched on, but the covariates they are missing are not used in computing their match. 
In this option, the underlying algorithm works by replacing each missing value with a unique value, so that in the matching procedure, those covariates simply don't have a match because their
values are not equl to any other values.