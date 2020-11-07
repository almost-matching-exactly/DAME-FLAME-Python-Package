---
layout: default
title: Algorithm Controls
nav_order: 6
permalink: /user-guide/Algorithm-Controls
parent: User Guide
---

# Early Stopping Controls
{: .no_toc }

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

This goes in the Algorithm Controls page. 

## Introduction to Early Stopping Controls

The ideal situation for matching in causal inference is if each treatment unit has an exactly identical control unit. We can best determine the rise in income that a person experiences after a job training program if that person has an identical twin with the same degree and GPA as them who didn't attend the job training program. 

The `FLAME-DAME` package begins by matching identical twins ("exact matches") in the dataset. Since not all units have exact matches, most units are matched based on subsets of all covariates. The subset that a unit is matched on is the subsets that is selected to be most predictive of their outcome. 

As the FLAME and DAME algorithms run, the units that are matched later in the algorithm, are those that are most distinct in observable characteristics from the other units in the dataset are matched later. Later matched units are likely to have the highest error in estimated treatment effects. For this reason, there are situations where the FLAME or DAME algorithm should be stopped early in order to avoid poor matches. 


## Recommendations


The default option is that the algorithm runs until all units are matched. However, if runtime or high accuracy of estimates of treatment effects are important, then we recommend users experiment with their stopping criteria based on their specific need and dataset size. A large dataset will have a longer runtime, and an early stop will take less time. Regardless of the early stopping criteria chosen, in the majority of datasets, any early stopping will lead to closer estimates between the estimated and true treatment effects. This is illustrated in the examples section. 

If it is crucial that all units be matched, it is recommended that users do not use any early stopping criteria.

| Category of Early Stopping              | Technical Details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Usage Recommendation                                                                                                                                                                                                                                                                                                                                                                         | Algorithm parameters                           |
|-----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------|
| Algorithm Iterations                    | This provides a number of iterations after which to stop the DAME or FLAME algorithm. If FLAME is used, then this is the maximum number of covariates that can be dropped, meaning when the total number of covariates is $m$, no unit will be matched on $m-$`early_stop_iterations`  covariates                                                                                                                                                                                                              | This is useful in the case of a FLAME user knowing their preferred covariate match size, or if a user knows what runtime is sufficient from a previous experiment                                                                                                                                                                                                                            | `early_stop_iterations`                        |
| Unmatched Units in Treatment or Control | When the algorithm is set with the `repeats=True` parameter, then previously matched units can still be placed in groups with other units. The algorithm will by default stop iterating when there are no more units that have not been placed in any group. However, a case could arise where all units remaining to be placed in a group are of the treatment or control group, and we  provide this option in case a user has preference between ensuring that all treated or control units are matched.  | These parameters will not be useful, and is therefore not recommended in the case where the the `repeats` parameter is False. If `repeats=False`, then in effect, both of these parameters are True.                                                                                                                                                                                                        |   `stop_unmatched_c`, `stop_unmatched_t`       |
| Proportion of unmatched units           | This stops the algorithm when some fraction of control units or treatment units are unmatched                                                                                                                                                                                                                                                                                                                                                                                                                | One specific case in which this could be useful immediately is where a user is certain that some percent of the input is unlikely to result in good matches.                                                                                                                                                                                                                                 | `early_stop_un_c_frac`, `early_stop_un_t_frac` |
| Predictive Error                        | The predictive error measures how important a covariate set is for predicting the outcome on the holdout dataset, using a machine learning algorithm. It is the sole determinant of the covariate set to match on for DAME, and one of two factors for FLAME.                                                                                                                                                                                                                                                | The range of this value is specific to a dataset's values. Therefore, reasonable values for this can only be determined after at least one prior run of this algorithm on the same dataset in which the predictive error is observed.                                                                                                                                                        | `early_stop_pe`, `early_stop_pe_frac`          |
| Balancing Factor                        | The balancing factor of an iteration is the number of matches formed after selecting a covariate set, and the discrepancy between the number of treated and control units remaining to be matched after the matching. This is only part of the algorithm's decision of which covariates to drop for FLAME but is still measured for DAME.                                                                                                                                                                    | If it's important to a user that there be a balance between treatment and control units in each covariate set, this is  a parameter to pay attention to.  The range of this value is specific to a dataset's values. Therefore, reasonable values for this can only be determined  after at least one prior run of this algorithm on the same dataset, while observing the balancing factor. | `early_stop_bf`, `early_stop_bf_frac`          |
