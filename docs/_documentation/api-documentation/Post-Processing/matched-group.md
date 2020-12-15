---
layout: default
title: Matched Group
nav_order: 3
permalink: /api-documentation/post-processing/matched-group
parent: Post Processing
grand_parent: API Documentation
---

# dame_flame.utils.post_processing.MG
{: .no_toc }
 
The matched group of a unit


<div class="code-example" markdown="1">
```python
MG(matching_object, unit_ids, output_style=1)
```
</div>
<div id="source" class="language-markdown highlighter-rouge">
  <a class="number" href="#SourceCode"></a> 
  <a href="https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package/blob/master/dame_flame/utils/post_processing.py#L27">
    <h6><u>Source Code</u></h6>
  </a>
</div>

Uses the matches created by the FLAME and DAME algorithms to provide main matched groups of units.

Read more about matched groups in the [User Guide](../user-guide/Getting-Matches.html)


| Parameter Name   | Type | Description |
|------------------|---------------------------------------------|---------|
| matching_object | {dame_flame.matching.DAME, dame_flame.matching.FLAME} | The matching object used to run DAME and FLAME, after the .fit() and .predict() methods have been called to create the matches. If the matching_object's parameter for `verbose` is not 0, then as units without matches appear, the function will print this. |
| unit_ids | {int, list} | A unit id or list of unit ids | 
| output_style | int: {0,1} (default=1) | If 1, the covariates which were not used in matching for the group of the unit will have a "*" rather than the covariate value. Otherwise, it will output all covariate values. |

| Return Name | Type | Description  |
|-------------|------| --------------------------------------------------------------------|
| MMGs    | {list, dataframe, np.nan} | If one unit id was provided, this is a single dataframe containing the main matched group of the unit. If the unit does not have a match, the return will be np.nan. If multiple unit ids were provided, this will be a list of dataframes with the main matched group of each unit provided. If any unit does not have a match, rather than a dataframe, at its place will be np.nan. |


## Quick Example

```python
import pandas as pd
import dame_flame
df = pd.DataFrame([[0,1,1,1,0,5], [0,1,1,0,0,6], [1,0,1,1,1,7], [1,1,1,1,1,7]], 
                  columns=["x1", "x2", "x3", "x4", "treated", "outcome"])

model = dame_flame.matching.DAME()
model.fit(df)
result = model.predict(df)

mmg = dame_flame.utils.post_processing.MG(model, 0)
```
