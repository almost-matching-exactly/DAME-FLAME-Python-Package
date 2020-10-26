---
layout: default
title: Missing Data Handling
nav_order: 4
permalink: /documentation/user-guide/Missing-Data
parent: User Guide
grand_parent: Documentation
has_children: true
---

# Missing Data Handling
{: .no_toc }

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## Introduction to Missing Data Problems in Matching

Missing data is a complicated issue in matching problems. Imputing missing values on datasets is possible, but matches become less interpretable when matching on imputed values, in that it is more difficult to discern why a match was recommended by the matching algorithm.

The DAME and FLAME algorithms rely on covariate matching, so the `DAME-FLAME` package is able to take advantage of this and allows users to match on raw values on data sets with missing data without imputing any data. The `DAME-FLAME` package also provides options for imputing data.


## Determining Which Missing Data Method Is Right For You

### Missing values in the input data

We recommend users set the parameter `missing_data_replace=2`, where units that have missing values are still matched on, but the covariates they are missing are not used in computing their match. In this option, the underlying algorithm works by replacing each missing value with a unique value, so that in the matching procedure, those covariates simply don't have a match because their values are not equl to any other values. It is not recommended to use MICE to impute on the matching dataset, as this would be very slow.

Users also have the option of imputing their data through any data imputation method of their choice, and then using their imputed dataset as the input data. 

| Method                                                     | Recommendation                               | Technical Details                                                                                                                                                                                                                                   | `missing_data_replace` parameter value |
|------------------------------------------------------------|----------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------|
| Do not match units with missing values                     | Only use if missing values indicate bad unit | Units in the input dataset that have missing data are dropped from the dataset prior to running  the algorithms finding the matches                                                                                                                 | 1                                      |
| Match units with missing values, but ignore missing values | Recommended for most cases                   | When pre-processing the input, we place a unique value in place of each missing data point. This will not match any other value,  so a unit will only be matched where it's non-missing covariates match the non-missing covariates of another unit | 2                                      |
| Impute missing values with MICE                            | Not recommended                              | Creates several imputed datasets and iterates over each to find a match according to each dataset. See below for details.                                                                                                                           | 3                                      |

### Missing values in the holdout data
The "holdout dataset", if provided, must have the exact same covariates as the input dataset. It is used when training and fitting a machine learning algorithm to determine the best covariates for predicting the outcome. Matches will always be done on the corresponding covariates, but only on the input dataset.

We recommend users set the parameter `missing_data_replace=1`, where units with missing values are dropped, and these units are not used in determining the best covariate set for predicting the outcome. This is the fastest option for the algorithm's runtime. The error of the predictions will vary depending on how large and informative the observed, non-missing dataset is.

Users also have the option of imputing their data through any data imputation method of their choice, and then using their imputed dataset as the input data. 


| Method                                 | Recommendation                                                       | Technical Details                                                                                                                                                                                   | `missing_holdout_replace` parameter value |
|----------------------------------------|----------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| Do not match units with missing values | Recommended                                                          | Units in the holdout dataset that have missing data are dropped from the dataset prior to running  the algorithms finding the matches                                                               | 1                                         |
| Impute missing values with MICE        | Recommended if interpretability and speed are lower order priorities | Creates several imputed holdout datasets.  When choosing the best covariate set for predicting the outcome, iterates over each imputed dataset, and averages the predictive error over all datasets |   2                                       |


## Further Details on MICE imputation

The built-in imputation method that we include is  the "Multiple Imputation by Chained Equations" algorithm. This constructs several imputed datasets. It fills in missing values multiple times, creating multiple "complete" datasets. The error of the imputations, and the consistency of the imputations across imputed datasets, is dependent on how predictive the observed data is of the missing values. 

The underlying MICE implementation is done using scikit learn's experimental IterativeImpute package, and relies on DecisionTreeRegressions in the imputation process, to ensure that the data generated is fit for unordered categorical data. 

###### [](#header-6)Further Reference

For further reference on the MICE missing data handling technique, we recommend [Azur, Melissa J., et al. "Multiple imputation by chained equations: what is it and how does it work?."](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3074241/).