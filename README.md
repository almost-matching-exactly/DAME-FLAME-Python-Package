
<!-- Comment hi.  -->
# DAME (Dynamic Almost Matching Exactly) and FLAME (Fast Large-scale Almost Matching Exactly)
--------------------------------------------------

## Overview of the DAME and FLAME algorithms

The **FLAME** algorithm provides a fast and large-scale matching approach to causal inference. **FLAME** quickly creates matches that include as many covariates as possible by iteratively dropping covariates that are successively less useful for predicting outcomes based on matching quality. 

The **DAME** algorithm provides high-quality interpretable matches in causal inference. **DAME** creates matches of units that include as many covariates as possible by creating a heirarchy of covariate combinations on which to match, in the process solving an optimization problem for each unit in order to construct optimal matches. 

Both **DAME** and **FLAME** are available for categorical covariates only. 

A **Hybrid FLAME-DAME** algorithm will use FLAME to quickly remove less relevant features, and then switch to DAME for its high-quality interpretable matches. This is recommended for datasets with many features. It scales well, without noticable loss in the quality of matches. 

Both algorithms work well for data that fits in memory, and have thus far been tested on data sized up to 30,000 rows and 15 columns, which takes roughly 30 seconds on `FLAME` and roughly 45 seconds on `DAME`. An implementation for extremely large data sets will be provided at a later time. This implementation does include a variety of options for missing data handling.

For more details about these algorithms, please refer to their papers: [FLAME: A Fast Large-scale Almost Matching Exactly Approach to Causal Inference](https://arxiv.org/abs/1707.06315) and [Interpretable Almost-Exact Matching for Causal Inference](https://arxiv.org/abs/1806.06802)

Please reach out to let our team know if you're using this, or if you have any questions! Contact Neha Gupta at neha.r.gupta "at" duke "dot" edu 

## Installation

First, download from PyPi via
$ pip install dame-flame

``` Python

# import package
import dame_flame

# Run DAME
df = pd.read_csv("dame_flame/data/sample.csv")
model = dame_flame.matching.DAME(repeats=False, verbose=1, early_stop_iterations=False)
model.fit(holdout_data=df)
```

## Required data format

The `DAME-FLAME` package requires input data to have specific format. The input data can be either a file, or a **Python Pandas Data Frame**. However, all covariates in the input data should be categorical covariates, represented as an *integer* data type. If there are continuous covariates, please consider regrouping. In addition to input data columns, the input data must contain (1) A column indicating the outcome variable as an *integer* or *float* data type, and (2) A column specifying whether a unit is treated or control (treated = 1, control = 0) as an *integer* data type. There are no requirements for input data column names or order of columns. Below is an example of input data with n units and m covariates.


*Column-name / unit-id*  | x_1 | x_2 |...| x_m | outcome | treated
--- | --- | --- | --- | --- | --- | --- |
**1** | 2 | 3 | ... | 4 | 9 | 0
**2** | 1 | 3 | ... | 3 | 5.5 | 1
**3** | 1 | 4 | ... | 5 | -1 | 0
... | ... | ... | ... | ... | ... | ...
**n** | 0 | 5 | ... | 0 | 1 | 1
*Data Type*| *integer* | *integer* | *integer* | *integer* |  *numeric* | *0 or 1* |

The holdout training set, if provided, should also follow the same format.


## Other requirements

1.  `DAME-FLAME` requires installation of python, specifically with at least python 3.* version. If your computer system does not have python 3.*, install from [here](https://www.python.org/downloads/).

2. Dependencies on the following packages: Pandas, Scikit learn, Numpy. If your python version does not have these packages, install from [here](https://packaging.python.org/tutorials/installing-packages/)

## Example

We run the DAME function with the following basic command. In this example, we provide only the basic inputs: (1) input data as a dataframe or file, (2) the name of the outcome column, and (3) the name of the treatment column.

In this example, because of the toy sized small dataset, we set the holdout dataset equal to the complete input dataset.
```Python
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

print(model.groups_per_unit)
#> 0    1.0
#> 1    1.0
#> 2    1.0
#> 3    1.0

print(model.units_per_group)
#> [[2, 3], [0, 1]]

```
result is type **Data Frame**. The dataframe contains all of the units that were matched, and the covariates and corresponding values, that it was matched on. 
The covariates that each unit was not matched on is denoted with a " * " character.

model.groups_per_unit is a **Data Frame** with a column of unit weights which specifies the number of groups that each unit was placed in. 

model.units_per_group is a **list** in which each list is a main matched group, and the unit ids that belong to that group.

Additional values based on additional optional parameters can be retrieved, detailed in additional documentation below. 

To find the main matched group of a particular unit or group of units after DAME has been run, use the function *MG*:

```Python
mmg = dame_flame.utils.post_processing.MG(matching_object=model, unit_id=0)
print(mmg)

#>      x1    x2    x3    x4    treated    outcome
#> 0    0     1     1     *     0          5
#> 1    0     1     1     *     1          6
```

To find the conditional treatment effect (CATE) for the main matched group of a particular unit or group of units, use the function *CATE*:


```Python
te = dame_flame.utils.post_processing.CATE(matching_object=model, unit_id=0)
print(te)
#> 3.0
```

To find the average treatment effect (ATE) or average treatment effect on the treated (ATT), use the functions *ATE* and *ATT*, respectively:


```Python
ate = dame_flame.utils.post_processing.ATE(matching_object=model)
print(ate)
#> 2.0

att = dame_flame.utils.post_processing.MG(matching_object=model)
print(att)
#> 2.0
```

## DAME and FLAME Parameters and Defaults

```Python
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

```Python
# The main matched group of a unit or list of units
MG(matching_object, unit_ids)

# The conditional average treatment effect for a unit or list of units
CATE(matching_object, unit_ids)

# The average treatment effect for the matching data
ATE(matching_object)

# The average treatment effect on the treated for the matching data
ATT(matching_object)

```

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
