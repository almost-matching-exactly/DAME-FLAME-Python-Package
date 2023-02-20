---
layout: default
title: DAME
nav_order: 1
permalink: /api-documentation/DAME
parent: API Documentation
---

# dame_flame.matching.DAME
{: .no_toc }
 
<div class="code-example" markdown="1">
```python
class dame_flame.matching.DAME(adaptive_weights='ridge', alpha=0.1, 
         repeats=True, verbose=2, early_stop_iterations=float('inf'), 
         stop_unmatched_c=False, early_stop_un_c_frac=False, 
         stop_unmatched_t=False, early_stop_un_t_frac=False, 
         early_stop_pe=0.05,
         missing_indicator=np.nan, missing_data_replace=0, 
         missing_holdout_replace=0, missing_holdout_imputations=10, 
         missing_data_imputations=1, want_pe=False, want_bf=False)    
```
</div>
<div id="source" class="language-markdown highlighter-rouge">
  <a class="number" href="#SourceCode"></a> 
  <a href="https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/blob/master/dame_flame/matching.py#L130">
    <h6><u>Source Code</u></h6>
  </a>
</div>

This class creates the matches based on the DAME "Dynamic Almost Matching Exactly" algorithm. It has built in support for stopping criteria and missing data handling. 

Read more in the [User Guide](../user-guide/Getting-Matches.html)

## Parameters

| Parameter Name   | Type                                        | Default | Description                                                         |
|------------------|---------------------------------------------|---------|---------------------------------------------------------------------|
| adaptive_weights | {bool, 'ridge', 'decisiontree', 'ridgeCV', 'decisiontreeCV'} | 'ridge' | The method used to decide what covariate set should be dropped next. |
| alpha | float | 0.1 | If adaptive_weights is set to ridge, this is the alpha for ridge regression. | 
| repeats | bool | True | Whether or not units for whom a main matched has been found can be used again, and placed in an auxiliary matched group. |
| verbose | int: {0,1,2,3} | 2 | Style of printout while algorithm runs. If 0, no output. If 1, provides iteration number. If 2, provides iteration number and additional information on the progress of the matching at every 10th iteration. If 3, provides iteration number and additional information on the progress of the matching at every iteration |
| early_stop_iterations | {float,int} | float('inf') | A number of iterations after which to hard stop the algorithm. The default is infinite; i.e. no early stopping is done. Iterations start at 0 so setting early_stop_iterations to 0, for example, implies that only exact matches should be made. |
| stop_unmatched_c | bool | False | If True, then the algorithm terminates when there are no more control units to match. |
| stop_unmatched_t | bool | False | If True, then the algorithm terminates when there are no more treatment units to match. |
| early_stop_un_c_frac | float |  0.1 | Must be between 0.0 and 1.0. This provides a fraction of unmatched control units. When the threshold is met, the algorithm will stop iterating. For example, using an input dataset with 100 control units, the algorithm will stop when 10 control units are unmatched and 90 are matched (or earlier, depending on other stopping conditions). |
| early_stop_un_t_frac | float | 0.1 | Must be between 0.0 and 1.0. This provides a fraction of unmatched treatment units. When the threshold is met, the algorithm will stop iterating. For example, using an input dataset with 100 treatment units, the algorithm will stop when 10 control units are unmatched and 90 are matched (or earlier, depending on other stopping conditions). | 
| early_stop_pe| float | 0.05 | If DAME attempts to drop a covariate set that would raise the PE above (1 + early_stop_pe) times the baseline PE (the PE before any covariates have been dropped), DAME terminates before dropping this covariate set.|
| want_pe | bool | False | If true, the output of the algorithm will include the predictive error of the covariate sets used for matching in each iteration. |
| want_bf | bool | False | If true, the output will include the balancing factor for each iteration. |
| missing_indicator | {character, integer, numpy.nan} | numpy.nan | This is the indicator for missing data in the dataset. |
| missing_holdout_replace | int: {0,1,2} | 0 | If 0, assume no missing holdout training data and proceed. If 1, the algorithm excludes units with missing values from the holdout dataset. If 2, do MICE on holdout dataset. If this option is selected, it will be done for a number of iterations equal to missing_holdout_imputations. |
| missing_data_replace | int: {0,1,2,3} | 0 | If 0, assume no missing data in matching data and proceed. If 1, the algorithm does not match on units that have missing values. If 2, prevent all missing_indicator values from being matched on. If 3, do MICE on matching dataset. This is not recommended. If this option is selected, it will be done for a number of iterations equal to missing_data_imputations. |
| missing_holdout_imputations | int | 10 | If missing_holdout_replace=2, the number of imputations. |
| missing_data_imputations | int | 1 | If missing_data_replace=3, the number of imputations. |

## Attributes

| Attribute Name   | Type                                        | Description                                                         |
|------------------|---------------------------------------------|---------------------------------------------------------------------|
| units_per_group | Array | This is an array of arrays. Each sub-array is a matched group, and each item in each sub-array is an int, indicating the unit in that matched group. If matching is done with `repeats=False` then no unit will appear more than once. If `repeats=True` then the first group in which a unit appears is its main matched group. |
| df_units_and_covars_matched | dataframe | This is the resulting matches of DAME. Each matched unit is in this array, and the covariates they were matched on have the value used to match. The covariates units were not matched on are indicated with a `*` |
| groups_per_unit | Array | The length of this is equal to the number of units in the input array. Each item in this array corresponds to the number of times that each item was matched. If matching is done with repeats=False, then this number will be either 0 or 1. |
| bf_each_iter | Array | if `want_bf` parameter is True, this will contain the balancing factor of the chosen covariate set at each iteration |
| pe_each_iter | Array | if `want_pe` parameter is True, this will contain the predictive error of the chosen covariate set at each iteration |



## Quick Example

```python
import pandas as pd
import dame_flame
df = pd.DataFrame([[0,1,1,1,0,5], [0,1,1,0,0,6], [1,0,1,1,1,7], [1,1,1,1,1,7]], 
                  columns=["x1", "x2", "x3", "x4", "treated", "outcome"])
model = dame_flame.matching.DAME()
model.fit()
result = model.predict()
print(result)
#>    x1   x2   x3   x4
#> 0   *   1    1    1     
#> 1   *   1    1    *     
#> 2   *   *    1    1     
#> 3   *   1    1    1 
```

## Methods

| `fit(self, holdout_data, treatment_col....)`  | Provide self with holdout training data      |
| `predict(self, input_data...)`                | Perform the match on the input data |

<div class="code-example" markdown="1">
```python
__init__(adaptive_weights='ridge', alpha=0.1, repeats=True, verbose=2, early_stop_iterations=float('inf'), 
stop_unmatched_c=False, early_stop_un_c_frac=False, stop_unmatched_t=False, early_stop_un_t_frac=False,
early_stop_pe=0.05, 
missing_indicator=np.nan, missing_data_replace=0, missing_holdout_replace=0, 
missing_holdout_imputations=10, missing_data_imputations=1, want_pe=False, want_bf=False)
```
</div>
<div id="source" class="language-markdown highlighter-rouge">
  <a class="number" href="#SourceCode"></a> 
  <a href="https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/blob/master/dame_flame/matching.py#L71">
  <h6><u>Source Code</u></h6>
  </a>
</div>

Initialize self

<div class="code-example" markdown="1">
```python
fit(self, holdout_data=False, treatment_column_name='treated', outcome_column_name='outcome'
weight_array=False))
```
</div>
<div id="source" class="language-markdown highlighter-rouge">
  <a class="number" href="#SourceCode"></a> 
  <a href="https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/blob/master/dame_flame/matching.py#L99">
  <h6><u>Source Code</u></h6>
  </a>
</div>

Provide self with holdout training data

| `fit` Parameter Name   | Type                                        | Default | Description                                                         |
|------------------|---------------------------------------------|---------|---------------------------------------------------------------------|
| holdout_data | {string, dataframe, float, False } | False | This is the holdout training dataset. If a string is given, that should be the location of a CSV file to input. If a float between 0.0 and 1.0 is given, that corresponds the percent of the input dataset to randomly select for holdout data. If False, the holdout data is equal to the entire input data. |  
| treatment_column_name | string | "treated" | This is the name of the column with a binary indicator for whether a row is a treatment or control unit. |
| outcome_column_name | string | "outcome" | This is the name of the column with the outcome variable of each unit. |
| adaptive_weights | {bool, "ridge", "decisiontree", "ridgeCV", "decisiontreeCV"} | "ridge" | The method used to decide what covariate set should be dropped next. |
| weight_array | array | optional | If adaptive_weights = False, these are the weights to the covariates in input_data, for the non-adaptive version of DAME. Must sum to 1. In this case, we do not use machine learning for the weights, they are manually entered as weight_array. |

<div class="code-example" markdown="1">
```python
predict(self, input_data)
```
</div>
<div id="source" class="language-markdown highlighter-rouge">
  <a class="number" href="#SourceCode"></a> 
  <a href="https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/blob/master/dame_flame/matching.py#L134s">
  <h6><u>Source Code</u></h6>
  </a>
</div>

Perform match and return matches

| `predict` Parameter Name   | Type  | Default | Description |
|--------------|------------------|--------- | ---- |
| input_data | {string, dataframe} | Required Parameter | The dataframe on which to perform the matching, or the location of the CSV with the dataframe |  

| `predict` Return | Description  |
|-------------|-----------------------------------------------------------------------------------------------|
| Result    | Pandas dataframe of matched units and covariates matched on, with a "*" at each covariate that a unit did not use in matching                        |

<div class="language-markdown highlighter-rouge">
  <h4>Further Readings</h4>
  <br/>
  <a href="https://arxiv.org/abs/1806.06802">
    Liu, Dieng, et al. <i>Interpretable Almost Matching Exactly For Causal Inference</i>.
  </a>
</div>
