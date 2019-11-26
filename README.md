
<!-- Comment hi.  -->
# DAME (Dynamic Almost Matching Exactly) and FLAME (Flast Large-scale Almost Matching Exactly)
--------------------------------------------------

## Overview of the DAME and FLAME algorithms

The **FLAME** algorithm provides a fast and large-scale matching approach to causal inference. **FLAME** creates matches that include as many covariates as possible, and iteratively drops covariates that are successively less useful for predicting outcomes based on matching quality. Currently the `FLAME` package applies to categorical data. 

The **DAME** algorithm provides high-quality interpretable matches in causal inference for categorical data. **DAME** creates matches of units that include as many covariates as possible by creating a heirarchy of covariate combinations on which to match, in the process solving an optimization problem for each unit in order to construct optimal matches. 

A **Hybrid FLAME-DAME** algorithm will use FLAME to quickly remove less relevant features, and then switch to DAME for its high-quality interpretable matches. This is recommended for datasets with many features. It scales well, without noticable loss in the quality of matches. 

Both algorithms work well for data that fits in memory, and have thus far been tested on data sized up to 30,000 rows and 15 columns, which takes roughly 30 seconds on `FLAME` and roughly 45 seconds on `DAME`. An implementation for extremely large data sets will be provided at a later time. This implementation does include a variety of options for missing data handling.

For more details about these algorithms, please refer to their papers: [FLAME: A Fast Large-scale Almost Matching Exactly Approach to Causal Inference](https://arxiv.org/pdf/1707.06315.pdf) and [Interpretable Almost-Exact Matching for Causal Inference](https://arxiv.org/abs/1806.06802)

## Installation

``` r
# This is all wrong. Update once I have it deployed and a link to show off. 

# Download from CRAN
install.packages("FLAME")

# Download from GitHub
devtools::install_github("chiarui424/FLAME") 
```

## Required data format

The `DAME-FLAME` package requires input data to have specific format. The input data can be either a file, or a **Python Pandas Data Frame**. However, all covariates in the input data should be categorical covariates, represented as an *integer* data type. If there are continuous covariates, please consider regrouping. In addition to input data columns, the input data must contain (1) An outcome variable as an *integer* or *float* data type, and (2) A variable specifying whether a unit is treated or control (treated = 1, control = 0) as an *integer* data type.There are no requirements for input data column names or order of columns. Below is an example of input data with n units and m covariates.


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

2. Dependencies on the following packages: Pandas, Scikit learn, Numpy. If your python version does not have these pacakges, install from [here](https://packaging.python.org/tutorials/installing-packages/)

## Example

We run DAME function with the following command. The required input is only the input data, as a csv file, or a Python data frame. In this example, we provide: (1) input data, (2) the name of the outcome column, and (3) the name of the treatment column.

The model defaulted to a ridge regression  computation of the best covariate set to match on, with an alpha of 0.1, and used 10% of the input data as the holdout data. 

```Python
result = DAME(input_data=sample_df, treatment_column_name="treated", outcome_column_name="outcome")
print(result[0])
#>    x1 x2 
#> 0  1  * 
#> 1  1  5 
#> 3  1  * 
```
result is a list of size 1, where the element in the list is of type **Data Frame**. The dataframe contains the units that were matched, and the covariates and corresponding values, that it was matched on. The covariates that each unit was not matched on is noted with a " * " character. 

To find the main matched group of a unit after DAME has been run, use the function *mmg_of_unit*

```Python
mmg = mmg_of_unit(result[0], 3, sample_df, output_style=2)
print(mmg)

#>    x1 outcome treated 
#> 0  1     2       1
#> 1  1     3       0
#> 3  1     9       0
```

To find the treatment effect of a unit, use the function *te_of_unit*


```Python
te = te_of_unit(result[0], 3, sample_df, output_style=2)
print(te)
#> 1.7
```


## Parameters and Defaults

```Python
DAME(input_data,
         treatment_column_name = 'treated', weight_array = [0.25, 0.05, 0.7],
         outcome_column_name='outcome',
         adaptive_weights='ridge', alpha = 0.1, holdout_data=False,
         repeats=True, verbose=0, want_pe=False, early_stop_iterations=False, 
         early_stop_unmatched_c=False, early_stop_un_c_frac = 0.1, 
         early_stop_unmatched_t=False, early_stop_un_t_frac = 0.1,
         early_stop_pe = False, early_stop_pe_frac = 0.01,
         want_bf=False, early_stop_bf=False, early_stop_bf_frac = 0.01,
         missing_indicator=np.nan, missing_data_replace=0,
         missing_holdout_replace=0, missing_holdout_imputations = 10,
         missing_data_imputations=0)

FLAME(input_data,
         treatment_column_name = 'treated', weight_array = [0.25, 0.05, 0.7],
         outcome_column_name='outcome',
         adaptive_weights=False, alpha = 0.1, holdout_data=False,
         repeats=True, verbose=0, want_pe=False, early_stop_iterations=False, 
         early_stop_unmatched_c=False, early_stop_un_c_frac = 0.1, 
         early_stop_unmatched_t=False, early_stop_un_t_frac = 0.1,
         early_stop_pe = False, early_stop_pe_frac = 0.01,
         want_bf=False, early_stop_bf=False, early_stop_bf_frac = 0.01, 
         pre_dame=False, missing_indicator=np.nan, missing_data_replace=0,
         missing_holdout_replace=0, missing_holdout_imputations = 10,
         missing_data_imputations=0)
```

### Key parameters

**input_data**: file, DataFrame, required  
This is the data being matched. This is henceforth referred to as the matching data. 

**treatment_column_name**: string, optional (default="treated")  
This is the name of the column with a binary indicator for whether a row is a treatment or control unit

**outcome_column_name**: string, optional (default="outcome")  
This is the name of the column with the outcome variable of each unit. 

**adaptive_weights**: bool, "ridge", "decision tree", optional (default="ridge")  
The method used to decide what covariate set is optimal to drop.

**weight_array**: array, optional  
If adaptive_weights = False, these are the weights to the covariates in the dataframe, for the non-adaptive version of DAME. Must sum to 1. 

**alpha**: float, optional (default=0.1)  
If adaptive_weights version is ridge, this is the alpha for ridge regression.

**holdout_data**: file, DataFrame, float between 0 and 1, optional (Default = 0.1)
If doing an adaptive_weights version of DAME, this is used to decide what covariates to drop. The default is to use 10% of the input_data set. Users can specify a percentage of the matching data set to use, or use a different file. If using a different file, that file needs to have all of the same column labels, including treatment and outcome columns.

**repeats**: Bool, optional (default=False)  
Whether or not values for whom a main matched has been found can be used again, and placed in an auxiliary matched group  


**verbose**: int 0,1,2,3 (default=0)  
Style of printout while algorithm runs. 
If 1, provides iteration number 
2 provides iteration number and number of units left to match on every 10th iteration
3 does this print on every iteration. 


**want_pe**: bool, optional (default=False)  
If true, the output of the algorithm will include the predictive error of the covariate sets matched on in each iteration.


**want_bf**: bool, optional (default=False)  
If true, the output will include the balancing factor of each iteration.


**pre_dame**: bool, integer, optional (default=False)  
This is only an option for FLAME, and will allow a user to run the Hybrid-FLAME-DAME algorithm. If an integer n is provided, then after n iterations of FLAME, the algorithm will switch to DAME.



### Parameters related to missing data handling



**missing_indicator**: character, integer, np.nan, optional (default=np.nan)  
This is the indicator for missing data in the dataset. 

**missing_holdout_replace**: int 0,1,2, optional (default=0)  
if 0, assume no missing holdout data and proceed
if 1, excludes units with a missing value from the holdout dataset
if 2, do MICE on holdout dataset for missing_holdout_imputatations number of imputations. This is not recommended. 

**missing_data_replace**: int 0,1,2,3, optional, (default=0)  
if 0, assume no missing data in matching data and proceed
if 1, does not match on units that have a missing value. 
if 2, skip all missing_indicator values from being matched on
if 3, do MICE on matching dataset for missing_data_imputatations, number of imputations

**missing_holdout_imputatations**: int, optional (default=10)  
If missing_holdout_replace=2, the number of imputations

**missing_data_imputations**: int, optional (default=0)  
If missing_data_replace=3, the number of imputations. 


###  Parameters related to early stopping criteria


**early_stop_iterations**: int, optional  (default=0)  
If provided, a number of iterations after which to hard stop the algorithm

**early_stop_unmatched_c**: bool, optional (default=False)  
If True, then early_stop_un_c_frac provides a fraction of unmatched control units. After this threshold is met, the algorithm will stop. 

**early_stop_unmatched_t**: bool, optional (default=False)  
If True, then early_stop_un_t_frac provides a fraction of unmatched control units. After this threshold is met, the algorithm will stop. 

**early_stop_un_c_frac**: float from 0.0 to 1.0, optional (default=0.1)  
If early_stop_unmatched_c is True, this provides a fraction of unmatched control/treatment units. When threshold met, the algorithm with stop iterating.

**early_stop_un_t_frac**: float from 0.0 to 1.0, optional (default=0.1)
If early_stop_unmatched_t is True, this provides a fraction of unmatched control/treatment units. When threshold met, the algorithm with stop iterating.

**early_stop_pe**: bool, optional (default=False)  
If this is true, then if the covariate set chosen to match on has a predictive error lower than the parameter early_stop_pe_frac, the algorithm will stop. 

**early_stop_pe_frac**: float, optional (default=0.01)  
If early_stop_pe is true, then if the covariate set chosen to match on has a predictive error lower than this value, the algorithm will stop.  

**early_stop_bf**: bool, optional (default=False)  
If this is true, then if the covariate set chosen to match on has a balancing factor lower than early_stop_bf_frac, then the algorithm will stop.

**early_stop_bf_frac**: float, optional (default=0.01)  
If early_stop_bf is true, then if the covariate set chosen to match on has a balancing factor lower than this value, then the algorithm will stop.
