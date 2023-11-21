---
layout: default
title: var_ATE
nav_order: 7
permalink: /api-documentation/post-processing/var_ATE
parent: Post Processing
grand_parent: API Documentation
---

# dame_flame.utils.post_processing.var_ATE
{: .no_toc }
 
The average treatment effect estimate of the data and its variance, implementing the variance found in 
Abadie, Drukker, Herr, and Imbens (The Stata Journal, 2004) assuming constant treatment effect and homoscedasticity. Note that the implemented estimator is NOT asymptotically normal and so in particular, asymptotically valid confidence intervals or hypothesis tests cannot be conducted on its basis.


<div class="code-example" markdown="1">
```python
var_ATE(matching_object)
```
</div>
<div id="source" class="language-markdown highlighter-rouge">
  <a class="number" href="#SourceCode"></a> 
  <a href="https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/blob/master/dame_flame/utils/post_processing.py#L240">
    <h6><u>Source Code</u></h6>
  </a>
</div>

Uses the matches created by the FLAME and DAME algorithms to provide estimates for the ATE and variance of the ATE of the dataset.


| Parameter Name   | Type | Description |
|------------------|---------------------------------------------|---------|
| matching_object | {dame_flame.matching.DAME, dame_flame.matching.FLAME} | The matching object used to run DAME and FLAME. This must be after the .fit() and .predict() methods have been called to create the matches. |


| Return Name | Type | Description  |
|-------------|------| --------------------------------------------------------------------|
| var    | {float}         | A float representing the variance estimate for the ATE estimate. |
| ATE    | {float} | A float representing the ATE estimate of the dataset. |


## Quick Example

```python
import pandas as pd
import dame_flame
df = pd.DataFrame([[0,1,1,1,0,5], [0,1,1,0,0,6], [1,0,1,1,1,7], [1,1,1,1,1,7]], 
                  columns=["x1", "x2", "x3", "x4", "treated", "outcome"])

model = dame_flame.matching.DAME()
model.fit(df)
result = model.predict(df)

var, ate = dame_flame.utils.post_processing.var_ATE(model)
```
