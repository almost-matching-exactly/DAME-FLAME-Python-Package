---
layout: default
title: FAQ and Vocabulary Guide
nav_order: 6
permalink: /FAQ
---


# FAQ and Vocabulary Guide
{: .no_toc }

---

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## Vocabulary Guide

We briefly define some of the terms we use interchangeably throughout this User Guide and in this documentation below.

| Unit, Observation, Individual | A participant in the research trial, in either the control group or treatment group, for whom we have an observed outcome                     |
| Covariate, Observed data, X's, Independent variables  | The data we observe which is not the treatment group or the outcome      |
|  Outcome, Y, Dependent variables               | The outcome variable of the research |
| Treated Unit | A unit which is in the treatment group |
| Treatment Effects | We have a whole page on this. See [here](https://almost-matching-exactly.github.io/DAME-FLAME-Python-Package/documentation/user-guide/Treatment-Effects). |
| Matched group, matches | The group that a unit is assigned to based on the result of the matching algorithm |
| Main matched group | If units are assigned to multiple groups, each group has one group which is its main group, in which it is matched to units which it is most similar to. Other groups it is in will have less similar covariates  |


## FAQ

### Why Don't You Support Continuous Data?
The `DAME-FLAME` package implements the DAME and FLAME algorithms, which are designed to find the best matches on datasets that are discrete. We believe this package will be useful for researchers regardless, due to the existence of several research problems that do rely on discrete data. 

### Why doesn't the machine learning step support my preferred method?
At this time, we have provided implementations for three options: ridge regressions with a pre-specified alpha, ridge regressions with cross validation, and decision trees. We chose these based on what we know researchers want at this time. We definitely would love to add more if you wish! Please see our contributing guide. 

### Why doesn't the package have any built-in visualization methods?
Visualizing data is a valuable tool to understanding it before and after performing any analysis like matching. While the `DAME-FLAME` package doesn't have built in functions to visualize the data, we provide several examples of ways that researchers could visualize any dataset, before and after matching. This is a listing:

- A histogram depicting the size of the matched group of each unit [here](https://almost-matching-exactly.github.io/DAME-FLAME-Python-Package/examples/flame_vs_dame_quality/)
- A scatter plot of true vs estimated CATT for units in a matched dataset [here](https://almost-matching-exactly.github.io/DAME-FLAME-Python-Package/examples/early_stopping/)
- A bar chart depicting the treatment effects of different matched groups [here](https://almost-matching-exactly.github.io/DAME-FLAME-Python-Package/examples/exact_matching/)
- A histogram depicting the size of each matched group [here](https://almost-matching-exactly.github.io/DAME-FLAME-Python-Package/examples/exact_matching/)
- A histogram of the number of units matched on each covariate, to help interpret covariate importance [here](https://almost-matching-exactly.github.io/DAME-FLAME-Python-Package/examples/interpretability/)

For each of these, we provide a link to our github repository, and encourage users to fork the code and visualize your own data. 

### Why should I use this instead of another package? Other ones seem more common!

We know lots of other matching algorithms are popular. We won't become more common unless people like you will consider using us anyways, and we hope you'll spread the word once you decide you like `DAME-FLAME` :) 

We believe that the algorithms other matching packages rely on result in low-quality, uninterpretable matches. We define low-quality matches as matches with poor treatment effect estimates, and uninterpretable matches as the inability to determine from a match which covariates influence the decision of matched units. The most popular matching algorithm is propensity score matching. Coarsened Exact Matching is another popular technique. Propensity score matching reduces a dataset to one dimension, so matches are produced without an aim of highlighting important covariates. Coarsened exact matching also pre-defines distance metrics, which will often be dominated by irrelevant covariates [(Dieng, et al.)](https://arxiv.org/abs/1806.06802). Causal Forests are gaining popularity too, but we claim that isn't a matching method in [Wang, et al.](https://arxiv.org/abs/1707.06315).

Please see our simulation [here](https://github.com/nehargupta/dame-flame-experiments/blob/master/DAME_vs_FLAME_vs_Matchit.ipynb) comparing `DAME-FLAME` against MatchIt's propensity score matching. This simulation shows that our package results in higher-quality matches.

Lastly, we hope you'll consider using `DAME-FLAME` when you compare the features of the `DAME-FLAME` package against other popular matching packages that implement the algorithms discussed above. We offer several built-in treatment effect estimators so that users don't have to rely on other packages or compute their own, and we offer built-in missing data handling. 