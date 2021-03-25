---
layout: default
title: Data Generating
nav_order: 5
permalink: /api-documentation/data-generating/
parent: API Documentation
---
# dame_flame.utils.data
Functions that generate data according to a distribution, returning the data and the true treatment effects of the values.

## dame_flame.utils.data.generate_uniform_given_importance
{: .no_toc }
 
Creates a dataset with covariates in a uniform distribution where the covariates' importance can be pre-specified by the user. The treatment effect will be normally distributed. 

<div class="code-example" markdown="1">
```python
generate_uniform_given_importance(num_control=1000, num_treated=1000,
                                  num_cov=4, min_val=0,
                                  max_val=3, covar_importance=[4, 3, 2, 1],
                                  bi_mean=2, bi_stdev=1)
```
</div>
<div id="source" class="language-markdown highlighter-rouge">
  <a class="number" href="#SourceCode"></a> 
  <a href="https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/blob/master/dame_flame/utils/data.py#L11">
    <h6><u>Source Code</u></h6>
  </a>
</div>

| Parameter Name   | Type | Description |
|------------------|---------------------------------------------|---------|
| num_control | integer | The number of units in the control group |
| num_treated | integer | The number of units in the treated group |
| num_cov | integer | The number of covariates |
| min_val | integer | The minimum value each covariate can take |
| max_val | integer | The maximum value each covariate can take |
| covar_importance | array | The importance each covariate has in determining the outcome. Must be of length num_cov |
| bi_mean | numerical | The treatment effect is normally distributed with this mean |
| bi_stdev | numerical | The treatment effect is normally distributed with this standard deviation |


| Return Name | Type | Description  |
|-------------|------| --------------------------------------------------------------------|
| data_frame    | Pandas Dataframe | A dataframe that is according to the specifications. Units 0 through num_treated are treatment group, and num_treated through num_treated+num_control are control group units. |
| true_catt    | array | The CATE of each treated unit, where the ith has the treatment effect of the ith unit in the dataframe.  |


## dame_flame.utils.data.generate_binomial_given_importance

{: .no_toc }
 
Creates a dataset with covariates in a binomial distribution where the covariates' importance on outcome can be pre-specified by the user. The treatment effect will be normally distributed. 

<div class="code-example" markdown="1">
```python
generate_binomial_given_importance(num_control=1000, num_treated=1000,
                                  num_cov=5, bernoulli_param=0.5,
                                  bi_mean=2, bi_stdev=1,
                                  covar_importance=[4, 3, 2, 1, 0.01])
```
</div>
<div id="source" class="language-markdown highlighter-rouge">
  <a class="number" href="#SourceCode"></a> 
  <a href="https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/blob/master/dame_flame/utils/data.py#L45">
    <h6><u>Source Code</u></h6>
  </a>
</div>

| Parameter Name   | Type | Description |
|------------------|---------------------------------------------|---------|
| num_control | integer | The number of units in the control group |
| num_treated | integer | The number of units in the treated group |
| num_cov | integer | The number of covariates |
| bernoulli_param | numerical | The bernoulli parameter determining the distribution of the covariates | 
| covar_importance | array | The importance each covariate has in determining the outcome. Must be of length num_cov |
| bi_mean | numerical | The treatment effect is normally distributed with this mean |
| bi_stdev | numerical | The treatment effect is normally distributed with this standard deviation |


| Return Name | Type | Description  |
|-------------|------| --------------------------------------------------------------------|
| data_frame    | Pandas Dataframe | A dataframe that is according to the specifications. Units 0 through num_treated are treatment group, and num_treated through num_treated+num_control are control group units. |
| true_catt    | array | The CATE of each treated unit, where the ith has the treatment effect of the ith unit in the dataframe.  |


## dame_flame.utils.data.generate_binomial_decay_importance

{: .no_toc }
 
Creates a dataset with covariates in a binomial distribution where the covariates' importance on outcome exponentially decays rather than being determined by the user. The treatment effect will be normally distributed. 

<div class="code-example" markdown="1">
```python
generate_binomial_decay_importance(num_control=1000, num_treated=1000,
                                  num_cov=5, bernoulli_param=0.5,
                                  bi_mean=2, bi_stdev=1)
```
</div>
<div id="source" class="language-markdown highlighter-rouge">
  <a class="number" href="#SourceCode"></a> 
  <a href="https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/blob/master/dame_flame/utils/data.py#L45">
    <h6><u>Source Code</u></h6>
  </a>
</div>

| Parameter Name   | Type | Description |
|------------------|---------------------------------------------|---------|
| num_control | integer | The number of units in the control group |
| num_treated | integer | The number of units in the treated group |
| num_cov | integer | The number of covariates |
| bernoulli_param | numerical | The bernoulli parameter determining the distribution of the covariates | 
| bi_mean | numerical | The treatment effect is normally distributed with this mean |
| bi_stdev | numerical | The treatment effect is normally distributed with this standard deviation |


| Return Name | Type | Description  |
|-------------|------| --------------------------------------------------------------------|
| data_frame    | Pandas Dataframe | A dataframe that is according to the specifications. Units 0 through num_treated are treatment group, and num_treated through num_treated+num_control are control group units. |
| true_catt    | array | The CATE of each treated unit, where the ith has the treatment effect of the ith unit in the dataframe.  |
