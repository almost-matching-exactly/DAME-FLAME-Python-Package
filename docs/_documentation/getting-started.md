---
layout: default
title: Getting Started
nav_order: 2
permalink: /getting-started
---
# Getting Started
{: .no_toc }
Here, we aim to get you launched
{: .fs-6 .fw-300 }

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## Dependencies
This package requires prior installation of
- Python (>= 3.0)
- NumPy (>= 1.17.5)
- Scikit-Learn (>= 0.22.1))
- Pandas (todo: check)

If your computer system does not have python 3.*, install from [here](https://www.python.org/downloads/).

If your python version does not have the Pandas, Scikit learn, or Numpy packages, install from [here](https://packaging.python.org/tutorials/installing-packages/)

## Installation
The DAME-FLAME Python Package is available for download on the [almost-matching-exactly Github](https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package) 
or via PyPi (recommended):

{% highlight markdown %}
pip install dame-flame
{% endhighlight %}

## Quickstart Example

We run the DAME function with the following basic command. In this example, we provide only the basic inputs: (1) input data as a dataframe or file, (2) the name of the outcome column, and (3) the name of the treatment column.

In this example, because of the toy sized small dataset, we set the holdout dataset equal to the complete input dataset.

<div class="code-example" markdown="1">
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

print(model.groups_per_unit)
#> 0    1.0
#> 1    1.0
#> 2    1.0
#> 3    1.0

print(model.units_per_group)
#> [[2, 3], [0, 1]]
```
</div>

result is type **Data Frame**. The dataframe contains all of the units that were matched, and the covariates and corresponding values, that it was matched on. 
The covariates that each unit was not matched on is denoted with a " * " character.

model.groups_per_unit is a **Data Frame** with a column of unit weights which specifies the number of groups that each unit was placed in. 

model.units_per_group is a **list** in which each list is a main matched group, and the unit ids that belong to that group.

Additional values based on additional optional parameters can be retrieved, detailed in additional documentation below. 

To find the main matched group of a particular unit or group of units after DAME has been run, use the function *MG*:

<div class="code-example" markdown="1">
```python
mmg = dame_flame.utils.post_processing.MG(matching_object=model, unit_id=0)
print(mmg)
#>      x1    x2    x3    x4    treated    outcome
#> 0    0     1     1     *     0          5
#> 1    0     1     1     *     1          6
```
</div>

To find the conditional treatment effect (CATE) for the main matched group of a particular unit or group of units, use the function *CATE*:

<div class="code-example" markdown="1">
```python
te = dame_flame.utils.post_processing.CATE(matching_object=model, unit_id=0)
print(te)
#> 3.0
```
</div>

To find the average treatment effect (ATE) or average treatment effect on the treated (ATT), use the functions *ATE* and *ATT*, respectively:

<div class="code-example" markdown="1">
```python
ate = dame_flame.utils.post_processing.ATE(matching_object=model)
print(ate)
#> 2.0
att = dame_flame.utils.post_processing.MG(matching_object=model)
print(att)
#> 2.0
```
</div>