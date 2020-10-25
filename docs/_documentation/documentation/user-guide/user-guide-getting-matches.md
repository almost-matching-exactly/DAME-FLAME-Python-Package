---
layout: default
title: Getting Matches
nav_order: 2
permalink: /documentation/user-guide/Getting-Matches
parent: User Guide
grand_parent: Documentation
has_children: true
---

# Getting Matches from the Data
{: .no_toc }

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>
This goes in the "Getting Matches" page, which possibly needs to be split up by algorithm into two pages.


## FLAME

FLAME stands for *Fast Large Scale Almost Matching Exactly*. The FLAME algorithm  begins  by  matching  any  units  that  can  be  matched  exactly  on  all  covariates.  The algorithm will iterate over all covariates until stopping criteria  is  reached.   In  each  iteration,  the  algorithm  will  drop the worst  covariate  set  to match on, and units that have identical values in all of the remaining covariates will form a matched group. When deciding which covariate should be dropped, at each step, it drops the covariate leading to the smallest drop in match quality, MQ, defined as MQ=C·BF−PE.  Here, PE denotes the predictive error, which measures how important the dropped covariate is for predicting the outcome on the holdout dataset, using a machine learning algorithm.  The balancing  factor, BF, measures the number of matches formed by dropping that covariate and the discrepancy between the number of treated and control units after the matching. In future iterations, the covariate that was determined worst and was just dropped will not reappear, so the maximum number of times the algorithm will iterate is equal to the number of covariates. 


```python
import pandas as pd
import dame_flame
df = pd.read_csv("dame_flame/data/sample.csv")
model = dame_flame.matching.FLAME(repeats=False, verbose=1, early_stop_iterations=False)
model.fit(holdout_data=df)
result = model.predict(input_data=df)
print(result)
#>    x1   x2   x3   x4
#> 0   0   1    1    *     
#> 1   0   1    1    *     
#> 2   1   0    *    1     
#> 3   1   0    *    1     
```

###### References
For more details on this algorithm, see 
[Wang, Tianyu, et al. "Flame: A fast large-scale almost matching exactly approach to causal inference."](https://arxiv.org/abs/1707.06315)


## DAME

DAME stands for *Dynamic Almost Matching Exactly*. The  algorithm  begins  by  matching  any  units  that  can  be  matched  exactly  on  all  co-variates.  The algorithm will iterate over options of covariates to match on until stopping criteria  is  reached.   In  each  iteration,  the  algorithm  will  select  the  best  covariate  set  to match on, and units that have identical values in all of the covariates that are part of the chosen covariate set will form a matched group. In its options of covariate sets to drop, DAME will always include the largest possible covariate sets, and will ultimately consider several combinations of covariates before selecting one to match on. It defines the best covariate set as the one that minimizes PE. PE is predictive error, and measures how important the covariate set is for predicting the outcome on the holdout dataset, using a machine learning algorithm


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

###### References
For more details on this algorithm, see 
[Dieng, Awa, et al. "Interpretable almost-exact matching for causal inference."](https://arxiv.org/abs/1806.06802)

## Hybrid FLAME-DAME


The hybrid algorithm works by ...
 (quick example)

###### References
For more details on this algorithm, see 
[Dieng, Awa, et al. "Interpretable almost-exact matching for causal inference."](https://arxiv.org/abs/1806.06802) 
 
## Variations in the learning of the best covariate set

Both the FLAME and DAME algorithms choose the best covariate set after measuring how important each covariate set is for predicting the outcome on the holdout dataset, using a machine learning algorithm. We offer different options for the machine learning algorithm used, as well as a simplified FLAME and simplified DAME that does not use machine learning.

| Learning Method     | Technical Details                                                                                                                                                                                                                                                                                    | Usage Recommendation                                                                                                                                                                                                                                                                                                                                                      | Algorithm parameter                |
|---------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| Ridge Regression    | A ridge regression is similar to an ordinary least squares regression,  but it imposes a penalty on the size of coefficients. It minimizes a  residual sum of squares. A shrinkage parameter, $\alpha$ must be included.                                                                             | This can only be used when it is certain that none of the covariates are categorical. Ordinal, binary, and discrete numerical  data is all accepted. For this option, a larger $\alpha$ corresponds should be chosen if it is believed that there is greater multicollinearity in the data, meaning that many covariates are linearly correlated.                         | `adaptive_weights='ridge'`         |
| Ridge Regression CV | This is a ridge regression with built-in cross validation to determine the best $\alpha$ parameter. We use the scikit-learn ridgeCV class, but the default array of $\alpha$ options that we provide the function to iterate over is larger  than the default they provide, for greater flexibility. | This also can only be used when it is certain that none of the covariates are categorical. Ordinal, binary and discrete numerical data is all accepted.  This option is advantageous over the 'ridge' option without cross validation in a case where a user is uncertain about the $\alpha$ parameter, and a minor  speed decrease from cross validation is acceptable.  |   `adaptive_weights='ridgeCV'`     |
| Decision Tree       | The underlying implementation is the Decision Tree Regression provided by scikit-learn, which uses a variation of CART. Trees predict the value of the outcome by learning decision rules from the covariates.                                                                                       | This can be used for categorical, ordinal, binary, and discrete numerical data.  Overfitting is a risk with decision tree models, which can be possible in DAME or FLAME algorithm if the holdout and input datasets provided are the same.                                                                                                                               | `adaptive_weights='decision-tree'` |

###### References
We use scikit-learn for the underlying learning algorithms. So we refer you to their documentation and references to learn more about these popular machine learning algorithms, as well as their specific implementations:

[Scikit-learn Ridge Regressions](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html).

[Scikit-learn RidgeCV](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.RidgeCV.html).

[Scikit-learn DecisionTree](https://scikit-learn.org/stable/modules/tree.html#tree).

For examples of categorical, binary, and numerical data, see [here](https://stats.idre.ucla.edu/other/mult-pkg/whatstat/what-is-the-difference-between-categorical-ordinal-and-numerical-variables/). 


## Fixed weights for a simplified version of DAME and FLAME
blah blah blaaaaaaaaah