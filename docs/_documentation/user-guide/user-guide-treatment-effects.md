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

We define and discuss the most common estimands that researchers use to quantify the effect of a treatment.

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

As an important note, these metrics will be biased if the unconfoundedness or ignorability assumption does not hold. In other words, it is best to use these metrics if the outcome is independent of the treatment conditioned on the observable covariates. For this reason, it can be good to include as many covariates as possible that may affect the outcome or selection into treatment.

In a case where a user is conflicted on whether or not to include a particular covariates, we recommend including it, running FLAME or DAME, and observing how quickly it is dropped via the `verbose=3` parameter. If the covariate is dropped in an early iteration with a low predictive error, it can be assumed that covariate is only weakly correlated with the outcome. Users can always match a second time after removing weakly correlated covariates from their dataset, if they wish. We recommend this approach, in order to ensure that any important covariates are matched on and that the bias of these resulting treatment effect estimators is minimized.

### Overlap of Treatment and Control Groups

A common problem in causal inference is that of overlap or imbalance between treatment and control groups. A treatment and control group have no overlap if none of their (discrete) covariates have the same values. In this setting, FLAME and DAME would not make any matches, and treatment effect estimation would not be possible. 

A more moderate issue is that of partial overlap, in which some units do not have matches. Because the `DAME-FLAME` package allows for algorithm controls, even if all units could be matched in theory, users of the algorithm might prefer to avoid matching all units. Regardless of the reason, units that are unmatched do not have a CATE estimate and they are not included in the ATE calculations. 


## Notation for Causal Inference

We index matched units by $i$, which ranges from 1 to $N$. We may interchangeably refer to the matched units as 'individuals' or 'observations', where we make implicit the fact that they have been matched; otherwise, they cannot contribute to treatment effect estimates.

There are $r$ pre-treatment covariates $x_1, \dots, x_r$ and for a given unit $i$, we will refer to its vector of covariates as $X_i$.

Let the treatment indicator for any unit $i$ be indicated as $T_i$. 

We let $Y_i$ be the observed outcome for individual $i$ where $Y_i = Y_i(1)T_i + Y_i(0)(1 - T_i)$ and $Y_i(0), Y_i(1)$ are the potential outcomes of unit $i$ under control and treatment, respectively.

Lastly, we introduce notation for matched groups, which we index by $m$, which ranges from 1 to $M$. The size of a matched group $m$ is $\| m\vert$, which is the number of units in the group.


## Conditional Average Treatment Effect (CATE)

This is defined as the average treatment effect conditional on particular covariates. Formally, the CATE given a set of covariates $X_i$ is: $\text{CATE}(X_i) = \frac{1}{N}\sum_{i=1}^N\mathbb{E}[Y(1)-Y(0)\|X_i]$

Our implementation of CATE estimation allows users to input a unit $i$ and receive its CATE, based off the covariates it was matched to other units on. 

Since our units are matched almost-exactly, all units in a given matched group will have the same CATE. For a unit $i$ in matched group $m$ of size $\|m\|$, with $\|m_0\|$ control units and $\|m_1\|$ treated units, we estimate the CATE of unit $i$ as: $$\frac{1}{\|m_1\|}\sum_{i:T_i=1}[\hat{Y}_i(1)]-\frac{1}{\|m_0\|}\sum_{i:T_i=0}[\hat{Y}_i(0)]$$ 

where $\hat{Y}_i(0), \hat{Y}_i(1)$ are estimated using the units in $m$ with treatment $1 - T_i$.


## Average Treatment Effect (ATE)

The Average Treatment Effect is defined to be: $\text{ATE} = \mathbb{E}[Y(1)-Y(0)]$. 

Let $q_i$ denote the number of matched groups that unit $i$ appears in. Note this quantity can be greater than 1 in case that matching is done with replacement, via the `Repeats = True` argument. We then define the weight of a matched group $m$: $w_m=\sum_{i=1}^{\|m\|}{q_i}$. Since the CATE of each unit in a group is the same, we can call the CATE of group $m$ $\text{CATE}_m$. 

We estimate ATE as: $\text{ATE} = \frac{\sum_{m}{\text{CATE_m} \times w_m}}{\sum_{m} w_m}$.

Note that this expression downweights units so that they do not dominate the ATE estimate.

<div class="language-markdown highlighter-rouge">
  <h4>Further Readings</h4>
  <br/>
  For more information on treatment effects, we recommend 
  <a href="https://www.mitpressjournals.org/doi/pdfplus/10.1162/003465304323023651?casa_token=fkH1Z_M2FG4AAAAA:MC8V9YAzYAn9YeT4cVvHQF0ZL12QsL8ZVFDX4juiQysLG5auaWyxdSzVrKINkH8nXwlN4P2r0wRq">
    Imbens, Guido W. <i>Nonparametric estimation of average treatment effects under exogeneity: A review</i>.
  </a>
</div>




