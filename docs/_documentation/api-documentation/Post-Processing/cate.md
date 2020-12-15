---
layout: default
title: CATE
nav_order: 5
permalink: /api-documentation/post-processing/CATE
parent: Post Processing
grand_parent: API Documentation
---


# dame_flame.utils.post_processing.CATE
{: .no_toc }
 
The conditional average treatment effect estimate of a subset of the data


<div class="code-example" markdown="1">
```python
CATE(matching_object, unit_ids)
```
</div>
<div id="source" class="language-markdown highlighter-rouge">
  <a class="number" href="#SourceCode"></a> 
  <a href="https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/blob/master/dame_flame/utils/post_processing.py#L85">
    <h6><u>Source Code</u></h6>
  </a>
</div>

Uses the matches created by the FLAME and DAME algorithms to provide CATE of subsets of the dataset.

Read more about Conditional Average Treatment Effect (CATE) estimates in the [User Guide](../user-guide/Treatment-Effects.html)


| Parameter Name   | Type | Description |
|------------------|---------------------------------------------|---------|
| matching_object | {dame_flame.matching.DAME, dame_flame.matching.FLAME} | The matching object used to run DAME and FLAME, after the .fit() and .predict() methods have been called to create the matches. If the matching_object's parameter for `verbose` is not 0, then as units without matches appear, the function will print this. |
| unit_ids | {int, list} | A unit id or list of unit ids | 


| Return Name | Type | Description  |
|-------------|------| --------------------------------------------------------------------|
| MMGs    | {list, float, np.nan} | If one unit id was provided, this is a single float representing the conditional average treatment effect of the unit. This is equal to the CATE of the group that the unit is in. If the unit does not have a match, the return will be np.nan. If multiple unit ids were provided, this will be a list of floats with the CATE of each unit provided. If any unit does not have a match, rather than a float within the list, at its place will be np.nan. |

## Quick Example

```python
import pandas as pd
import dame_flame
df = pd.DataFrame([[0,1,1,1,0,5], [0,1,1,0,0,6], [1,0,1,1,1,7], [1,1,1,1,1,7]], 
                  columns=["x1", "x2", "x3", "x4", "treated", "outcome"])

model = dame_flame.matching.DAME()
model.fit(df)
result = model.predict(df)

cate = dame_flame.utils.post_processing.CATE(model, 0)    
```
