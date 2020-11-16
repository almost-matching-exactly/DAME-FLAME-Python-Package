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
The FLAME and DAME algorithms use Hamming distance as the distance metric, which is only relevant for discrete data. If you have continuous data, we provide recommendations on discretizations here: [here](https://almost-matching-exactly.github.io/DAME-FLAME-Python-Package/documentation/user-guide/data-requirements).

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

The matches produced by the `dame-flame` package are higher quality. `dame-flame` doesn't use uninterpretable propensity scores, it matches on actual covariates. It doesn't require the user to specify the metric like CEM, since it uses machine learning to learn the metric adaptively. It is not based on a black box machine learning method like Causal Forest or BART, but it can often be just as accurate, and it’s much easier to troubleshoot! <a href="#references">[1]</a> <a href="#references">[2]</a>. You can see our simulation [here](https://github.com/nehargupta/dame-flame-experiments/blob/master/DAME_vs_FLAME_vs_Matchit.ipynb) comparing `dame-flame` against MatchIt’s propensity score matching. This simulation shows that our package results in higher-quality matches. Also, the features of the `dame-flame` package are really useful. We offer several built-in treatment effect estimators so that users don’t have to rely on other packages or compute their own, and we offer built-in missing data handling.

<div id="references" class="language-markdown highlighter-rouge">
  <h4>References</h4>
  <a class="number" href="#flame">[1]</a>
  <a href="https://arxiv.org/abs/1707.06315">
    Wang, Morucci, et al. <i>FLAME: A Fast Large-scale Almost Matching Exactly Approach to Causal Inference</i>.
  </a>
  <br/>
  <a class="number" href="#dame">[2]</a>
  <a href="https://arxiv.org/abs/1806.06802">
    Liu, Dieng, et al. <i>Interpretable Almost Matching Exactly For Causal Inference</i>.
  </a>
  <br/>
</div>