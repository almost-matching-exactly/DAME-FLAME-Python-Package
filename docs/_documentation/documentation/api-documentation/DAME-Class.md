---
layout: default
title: DAME
nav_order: 1
permalink: /documentation/api-documentation/DAME
parent: API Documentation
grand_parent: Documentation
---

# dame_flame.matching.DAME
{: .no_toc }
 
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
<div id="source" class="language-markdown highlighter-rouge">
  <a class="number" href="#SourceCode"></a> 
  <a href="https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/blob/master/dame_flame/matching.py#L79">
    <h6><u>Source Code</u></h6>
  </a>
</div>

This class creates the matches based on the DAME "Dynamic Almost Matching Exactly" algorithm. It has built in support for stopping criteria and missing data handling. 

Read more in the [User Guide](../user-guide/Getting-Matches.html)

## Parameters

| Parameter Name   | Type                                        | Default | Description                                                         |
|------------------|---------------------------------------------|---------|---------------------------------------------------------------------|
| adaptive_weights | {bool, 'ridge', 'decision tree', 'ridgeCV'} | 'ridge' | The method used to decide what covariate set should be dropped next. |
| alpha | float | 0.1 | If adaptive_weights is set to ridge, this is the alpha for ridge regression. | 
| repeats | bool | True | Whether or not units for whom a main matched has been found can be used again, and placed in an auxiliary matched group. |
| verbose | int: {0,1,2,3} | 2 | Style of printout while algorithm runs. If 0, no output. If 1, provides iteration number. If 2, provides iteration number and additional information on the progress of the matching at every 10th iteration. If 3, provides iteration number and additional information on the progress of the matching at every iteration |
| early_stop_iterations | int | 0 | If provided, a number of iterations after which to hard stop the algorithm. |
| stop_unmatched_c | bool | False | If True, then the algorithm terminates when there are no more control units to match. |
| stop_unmatched_t | bool | False | If True, then the algorithm terminates when there are no more treatment units to match. |
| early_stop_un_c_frac | float |  0.1 | Must be between 0.0 and 1.0. This provides a fraction of unmatched control units. When the threshold is met, the algorithm will stop iterating. For example, using an input dataset with 100 control units, the algorithm will stop when 10 control units are unmatched and 90 are matched (or earlier, depending on other stopping conditions). |
| early_stop_un_t_frac | float | 0.1 | Must be between 0.0 and 1.0. This provides a fraction of unmatched treatment units. When the threshold is met, the algorithm will stop iterating. For example, using an input dataset with 100 treatment units, the algorithm will stop when 10 control units are unmatched and 90 are matched (or earlier, depending on other stopping conditions). | 
| early_stop_pe | bool | False | If this is true, then if the covariate set chosen for matching has a predictive error higher than the parameter early_stop_pe_frac, the algorithm will stop. |
| early_stop_pe_frac | float | 0.01 | If early_stop_pe is true, then if the covariate set chosen for matching has a predictive error higher than this value, the algorithm will stop. |
| early_stop_bf | bool | False | If this is true, then if the covariate set chosen for matching has a balancing factor lower than early_stop_bf_frac, then the algorithm will stop.|
| early_stop_bf_frac | float | 0.01 | If early_stop_bf is true, then if the covariate set chosen for matching has a balancing factor lower than this value, then the algorithm will stop.|
| want_pe | bool | False | If true, the output of the algorithm will include the predictive error of the covariate sets used for matching in each iteration. |
| want_bf | bool | False | If true, the output will include the balancing factor for each iteration. |
| missing_indicator | {character, integer, numpy.nan} | numpy.nan | This is the indicator for missing data in the dataset. |
| missing_holdout_replace | int: {0,1,2} | 0 | If 0, assume no missing holdout data and proceed. If 1, the algorithm excludes units with missing values from the holdout dataset. If 2, do MICE on holdout dataset. If this option is selected, it will be done for a number of iterations equal to missing_holdout_imputations. |
| missing_data_replace | int: {0,1,2,3} | 0 | If 0, assume no missing data in matching data and proceed. If 1, the algorithm does not match on units that have missing values. If 2, prevent all missing_indicator values from being matched on. If 3, do MICE on matching dataset. This is not recommended. If this option is selected, it will be done for a number of iterations equal to missing_data_imputations. |
| missing_holdout_imputations | int | 10 | If missing_holdout_replace=2, the number of imputations. |
| missing_data_imputations | int | 1 | If missing_data_replace=3, the number of imputations. |


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

| `fit(self, holdout_data, treatment_col....)`  | Provide self with holdout data      |
| `predict(self, input_data...)`                | Perform the match on the input data |

<div class="code-example" markdown="1">
```python
__init__(adaptive_weights='ridge', alpha=0.1, repeats=True, verbose=2, early_stop_iterations=False, 
stop_unmatched_c=False, early_stop_un_c_frac=False, stop_unmatched_t=False, early_stop_un_t_frac=False,
early_stop_pe=False, early_stop_pe_frac=0.01, early_stop_bf=False, early_stop_bf_frac=0.01, 
missing_indicator=np.nan, missing_data_replace=0, missing_holdout_replace=0, 
missing_holdout_imputations=10, missing_data_imputations=1, want_pe=False, want_bf=False)
```
</div>
<div id="source" class="language-markdown highlighter-rouge">
  <a class="number" href="#SourceCode"></a> 
  <a href="https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/blob/master/dame_flame/matching.py#L36">
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
  <a href="https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/blob/master/dame_flame/matching.py#L69">
  <h6><u>Source Code</u></h6>
  </a>
</div>

Provide self with holdout data

| `fit` Parameter Name   | Type                                        | Default | Description                                                         |
|------------------|---------------------------------------------|---------|---------------------------------------------------------------------|
| holdout_data | {string, dataframe, float, False } | False | This is the holdout dataset. If a string is given, that should be the location of a CSV file to input. If a float between 0.0 and 1.0 is given, that corresponds the percent of the input dataset to randomly select for holdout data. If False, the holdout data is equal to the entire input data. |  
| treatment_column_name | string | "treated" | This is the name of the column with a binary indicator for whether a row is a treatment or control unit. |
| outcome_column_name | string | "outcome" | This is the name of the column with the outcome variable of each unit. |
| adaptive_weights | {bool, "ridge", "decision tree", "ridgeCV"} | "ridge" | The method used to decide what covariate set should be dropped next. |
| weight_array | array | optional | If adaptive_weights = False, these are the weights to the covariates in input_data, for the non-adaptive version of DAME. Must sum to 1. In this case, we do not use machine learning for the weights, they are manually entered as weight_array. |

<div class="code-example" markdown="1">
```python
predict(self, input_data)
```
</div>
<div id="source" class="language-markdown highlighter-rouge">
  <a class="number" href="#SourceCode"></a> 
  <a href="https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/blob/master/dame_flame/matching.py#L69">
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
