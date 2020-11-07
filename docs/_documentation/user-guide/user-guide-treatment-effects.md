---
layout: default
title: Treatment Effect Estimates
nav_order: 5
permalink: /user-guide/Treatment-Effects
parent: User Guide
mathjax: true
---

# Treatment Effect Estimates
{: .no_toc }

We define and discuss the most common metrics that researchers estimate when evaluating the results of a treatment.

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>


## Notes on Statistical Assumptions

### Unconfoundedness 

As an important note, these metrics will be biased if the unconfoundedness or ignorability assumption does not hold. In other words, it is best to use these metrics if the outcome is independent of the treatment when observable covaraiates are held constant. The bias will be as small as possible if many covariates are included, or users include any covariate that would have an impact on the outcome. 

In a case where a user is conflicted on whether or not to include a particular covariates, we recommend users consider including all variables and performing a match, while observing how quickly in the algorithm that covariate is dropped with the `verbose=3` parameter. If the covariate is dropped in an early iteration with a low predictive error, it can be assumed that covariate is only weakly correlated with the outcome. Users can then perform a match a second time after removing weakly correlated covariates from their dataset if they wish. We recommend this approach, in order to ensure that any important covariates are matched on and bias of these estimators is minimized.

### Overlap of Treatment and Control Groups

A common problem in causal inference is overlap or imbalance between treatment and control groups. A treatment and control group would have no overlap if none of the covariates have the same values. In this case, the FLAME and DAME algorithms would not find any matches, and no treatment effect estimates would be possible. 

A more moderate issue is partial overlap. In this case, some units do not have matches. Because the `DAME-FLAME` package allows for algorithm controls, even if all units could be matched in theory, users of the algorithm might prefer to avoid matching all units. Regardless of the cause, units that are unmatched do not have a CATE estimate, and they are not included in the ATE calculations either. 


## Standard Notation for Statistical Definitions

We refer to each matched unit as unit $i$. There are there are $N$ matched unit in total. We may interchangeably refer to the matched units as 'individuals' or 'observations', and although we will not always preface by saying they are 'matched units', please remember that they must be in order to be included in treatment effects. 

There are $r$ covariates upon which we have observed characteristics about each of the individuals prior to treatment, and these are $x_1$ through $x_r$. For a given unit $i$, its vector of covariates is $X_i$

Let the treatment indicator for any unit $i$ be indicated as $T_i$. 

We let $Y_i$ be the outcome for individual $i$. We use this interchangably with the notation $Y_i(T_i)$, so we write $Y_i(0)$ to indicate the outcome of $i$ if $i$ is in the control group, and $Y_i(1)$ if $i$ is in the treated group. 

Lastly, we introduce notation for the matched grous. We label a matched group as $m$. The size of a matched group is $\| m\vert$, and this is the number of units in the group. There are $M$ matched groups in total. 


## Conditional Average Treatment Effect (CATE)

This is defined as the average treatment effect conditional on particular covariates. We provide an implementation of CATE that allows a user to input a unit $i$, and then will output the CATE based on the covariates that $i$ was matched on. 

Formally, CATE for covariates $X_i$ is $\frac{1}{N}\sum_{i=1}^N\mathbb{E}[Y(1)-Y(0)\|X_i]$

Since our units are each matched in a group with other units that share treatment indicator as well as the opposite indicator, each unit in a matched group will have the same CATE. For a unit $i$ in matched group $M$ of size $\|\|M\|\|$, we estimate the CATE of $i$ as: $$\frac{1}{\|M\|}\sum_{i:T_i=1}[\hat{Y}_i(1)]-\frac{1}{\|M\|}\sum_{i:T_i=0}[\hat{Y}_i(0)]$$


## Average Treatment Effect (ATE)

The Average Treatment Effect for a population is generally $\mathbb{E}[Y(1)-Y(0)]$. 

We estimate this in a way that is robust to units reappearing in matched groups, according to the parameter `repeats=True`. Our estimate will ensure that units appearing in multiple matched groups are weighted accordingly, as well as that their influence in their groups is accounted for. 

Let $q_i$ denote the number of matched groups that unit $i$ appears in. Then, for a given matched group $m$, the number of matches made by the units in $m$ is $w_m=\sum_{i=1}^{\|m\|}\frac{1}{q_i}$. Since the CATE of each unit in a group is the same, we can call the CATE of group $m$ $\mathit{CATE}_m$. 

So, finally, we estimate ATE as $\frac{\sum_{m\in\mathbb{M}}CATE_m*w_m}{\sum_{m\in\mathbb{M}}w_m}$

<div class="language-markdown highlighter-rouge">
  <h4>Further Readings</h4>
  <br/>
  For more information on treatment effects, we recommend 
  <a href="https://www.mitpressjournals.org/doi/pdfplus/10.1162/003465304323023651?casa_token=fkH1Z_M2FG4AAAAA:MC8V9YAzYAn9YeT4cVvHQF0ZL12QsL8ZVFDX4juiQysLG5auaWyxdSzVrKINkH8nXwlN4P2r0wRq">
    Imbens, Guido W. <i>Nonparametric estimation of average treatment effects under exogeneity: A review</i>.
  </a>
</div>




