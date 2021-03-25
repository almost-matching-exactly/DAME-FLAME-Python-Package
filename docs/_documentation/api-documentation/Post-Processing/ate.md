---
layout: default
title: ATE
nav_order: 4
permalink: /api-documentation/post-processing/ATE
parent: Post Processing
grand_parent: API Documentation
---

# dame_flame.utils.post_processing.ATE
{: .no_toc }
 
The average treatment effect estimate of the data


<div class="code-example" markdown="1">
```python
ATE(matching_object)
```
</div>
<div id="source" class="language-markdown highlighter-rouge">
  <a class="number" href="#SourceCode"></a> 
  <a href="https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/blob/master/dame_flame/utils/post_processing.py#L135">
    <h6><u>Source Code</u></h6>
  </a>
</div>

Uses the matches created by the FLAME and DAME algorithms to provide ATE of the dataset.

Read more about Average Treatment Effect (ATE) in the [User Guide](../user-guide/Treatment-Effects.html)


| Parameter Name   | Type | Description |
|------------------|---------------------------------------------|---------|
| matching_object | {dame_flame.matching.DAME, dame_flame.matching.FLAME} | The matching object used to run DAME and FLAME. This must be after the .fit() and .predict() methods have been called to create the matches. |


| Return Name | Type | Description  |
|-------------|------| --------------------------------------------------------------------|
| ATE    | {float, np.nan} | A float representing the ATE of the dataset. If no units were matched, then the output will be np.nan. |


## Quick Example

```python
import pandas as pd
import dame_flame
df = pd.DataFrame([[0,1,1,1,0,5], [0,1,1,0,0,6], [1,0,1,1,1,7], [1,1,1,1,1,7]], 
                  columns=["x1", "x2", "x3", "x4", "treated", "outcome"])

model = dame_flame.matching.DAME()
model.fit(df)
result = model.predict(df)

ate = dame_flame.utils.post_processing.ATE(model)
```
