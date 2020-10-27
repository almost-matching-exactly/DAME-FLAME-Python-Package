---
layout: default
title: DAME
nav_order: 1
permalink: /documentation/api-documentation/DAME
parent: API Documentation
grand_parent: Documentation
has_children: true
---

# dame_flame.matching.DAME
{: .no_toc }
 
The DAME algorithm class

<div class="code-example" markdown="1">
```python
class dame_flame.matching.DAME(adaptive_weights='ridge', alpha=0.1, 
        repeats=True,
         verbose=2, early_stop_iterations=False, 
         stop_unmatched_c=False, early_stop_un_c_frac=False, 
         stop_unmatched_t=False, early_stop_un_t_frac=False, 
         early_stop_pe=False, early_stop_pe_frac=0.01, 
         early_stop_bf=False, early_stop_bf_frac=0.01,
         missing_indicator=np.nan, missing_data_replace=0, 
         missing_holdout_replace=0, missing_holdout_imputations=10, 
         missing_data_imputations=1, want_pe=False, want_bf=False)    
```
</div>

## Parameters

**adaptive_weights**: bool, "ridge", "decision tree", "ridgeCV", optional (default="ridge")  
The method used to decide what covariate set should be dropped next.

**alpha**: float, optional (default=0.1)  
If adaptive_weights is set to ridge, this is the alpha for ridge regression.

**repeats**: Bool, optional (default=True)  
Whether or not units for whom a main matched has been found can be used again, and placed in an auxiliary matched group. 

**verbose**: int 0,1,2,3 (default=2)  
Style of printout while algorithm runs.
If 0, no output 
If 1, provides iteration number 
If 2, provides iteration number and additional information on the progress of the matching at every 10th iteration
If 3, provides iteration number and additional information on the progress of the matching at every iteration

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

**want_pe**: bool, optional (default=False)  
If true, the output of the algorithm will include the predictive error of the covariate sets used for matching in each iteration.

**want_bf**: bool, optional (default=False)  
If true, the output will include the balancing factor for each iteration.

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

## References
[Dieng, Awa, et al. "Interpretable almost-exact matching for causal inference."](https://arxiv.org/abs/1806.06802)

## Example

```python
import pandas as pd
import dame_flame
df = pd.read_csv("dame_flame/data/sample.csv")
model = dame_flame.matching.DAME(repeats=False, verbose=1, early_stop_iterations=False)
model.fit(holdout_data=df)
result = model.predict(input_data=df)
print(result)
#>    x1   x2   x3   x4
#> 0   0   1    1    *     
#> 1   0   1    1    *     
#> 2   1   0    *    1     
#> 3   1   0    *    1     
```

## Methods

| __init__(self, adaptive_weights, alpha,...) | Initialize self                     |
| fit(self, holdout_data, treatment_col....)  | Provide self with holdout data      |
| predict(self, input_data...)                | Perform the match on the input data |

##### __init__(adaptive_weights='ridge', alpha=0.1, repeats=True, verbose=2, early_stop_iterations=False, stop_unmatched_c=False, early_stop_un_c_frac=False, stop_unmatched_t=False, early_stop_un_t_frac=False, early_stop_pe=False, early_stop_pe_frac=0.01, early_stop_bf=False, early_stop_bf_frac=0.01, missing_indicator=np.nan, missing_data_replace=0, missing_holdout_replace=0, missing_holdout_imputations=10, missing_data_imputations=1, want_pe=False, want_bf=False)

Initialize self

### fit(self, holdout_data=False, treatment_column_name='treated', outcome_column_name='outcome', weight_array=False))

Provide self with holdout data

### Parameters
**treatment_column_name**: string, optional (default="treated")
This is the name of the column with a binary indicator for whether a row is a treatment or control unit.

**outcome_column_name**: string, optional (default="outcome")
This is the name of the column with the outcome variable of each unit.

**adaptive_weights**: bool, "ridge", "decision tree", "ridgeCV", optional (default="ridge")
The method used to decide what covariate set should be dropped next.

**weight_array**: array, optional
If adaptive_weights = False, these are the weights to the covariates in input_data, for the non-adaptive version of DAME. Must sum to 1. In this case, we do not use machine learning for the weights, they are manually entered as weight_array.

### predict(self, input_data)

Perform match and return matches

| Parameters: | *input_data*: dataframe-like (default=None). The dataframe on which to perform the matching   |
|-------------|-----------------------------------------------------------------------------------------------|
| Returns:    | *Result*: Pandas dataframe of matched units and covariates matched on                         |
