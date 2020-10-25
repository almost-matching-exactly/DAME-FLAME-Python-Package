---
layout: default
title: Treatment Effect Estimates
nav_order: 3
permalink: /documentation/user-guide/Treatment-Effects
parent: User Guide
grand_parent: Documentation
has_children: true
mathjax: true
---

# Treatment Effect Estimates
{: .no_toc }

We define and discuss the most common metrics that researchers estimate when evaluating the results of a treatment.

As an important note, these metrics will be biased if the unconfoundedness or ignorability assumption does not hold. In other words, it is best to use these metrics if the outcome is independent of the treatment when observable covaraiates are held constant. The bias will be as small as possible if many covariates are included, or users include any covariate that would have an impact on the outcome. 

In a case where a user is conflicted on whether or not to include particular covariates, we provide an example here (todo: provide link) where the user includes all variables, and is able to eliminate weakly correlated covariates quickly and continue matching on only the most relevant ones. We recommend this approach, in order to ensure that any important covariates are matched on and bias of these estimators is minimized.

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## Standard Notation and Statistical Definitions

We say there are $i$ units or observations. These are the individuals being observed in the study. There are $n$ individuals in total.

There are $r$ covariates upon which we have observed characteristics about each of the individuals prior to treatment, and these are $x_1$ through $x_r$. For a given unit $i$, its vector of covariates is $X_i$

Let the treatment indicator for any unit $i$ be indicated as $T_i$. 

We let $Y_i$ be the outcome for individual $i$. We use this interchangably with the notation $Y_i(T_i)$, so we write $Y_i(0)$ to indicate the outcome of $i$ if $i$ is in the control group, and $Y_i(1)$ if $i$ is in the treated group. 

Lastly, we introduce notation for the matched group of a unit $i$. Supposed unit $i$ belongs in matched group $M$. We define the set of units in the opposite treatment group that unit $i$ is matched to as $\mathbb{J}_M(i)=\{\ell_1(i), ...\ell_M(i)\}$


## Average Treatment Effect (ATE)

The Average Treatment Effect for a population would be $\mathbb{E}[Y(1)-Y(0)]$. 

We estimate this for a sample as $\frac{1}{N}\sum_{i=1}^{N}[Y_i(1)-Y_i(0)]$. Since we only observe either $Y_i(1)$ or $Y_i(0)$ for each individual, the other is estimated from a unit's matched group. The imputed potential outcome is thus:

$$
\hat{Y}_i(0) =
\begin{cases}
Y_i & \text{if $T_i=0$} \\
\frac{1}{M}\sum_{j\in\mathbb{J}_M(i)}Y_j & \text{if $T_i=1$} \\
\end{cases}
$$

and


$$
\hat{Y}_i(1) =
\begin{cases}
Y_i & \text{if $T_i=1$} \\
\frac{1}{M}\sum_{j\in\mathbb{J}_M(i)}Y_j & \text{if $T_i=0$} \\
\end{cases}
$$

So finally, the ATE is estimated as $\frac{1}{N}\sum_{i=1}^{N}[\hat{Y}_i(1)-\hat{Y}_i(0)]$


## Average Treatment Effect on Treated (ATT)

The ATT is simply the ATE on exclusively treated units. Let $N_T=\sum_{i=1}^{N}W_i$. This is the number of treated units in the dataset. 

Formally, we estimate it similarly to the ATE described above, and it becomes: $\frac{1}{N_T}\sum_{i:T_i=1}[\hat{Y}_i(1)-\hat{Y}_i(0)]$

## Conditional Average Treatment Effect (CATE)

This is defined as the ATE conditional on particular covariates. In the DAME and FLAME algorithms, because each unit is not matched on all covariates, we provide an implementation of CATE that allows a user to input a unit $i$, and then will output the CATE based on the covariates that $i$ was matched on. 

Formally, CATE is $$\frac{1}{N}\sum_{i=1}^N\mathbb{E}[Y(1)-Y(0)\|X_i]$$

Since our units are each matched in a group with other units that share treatment indicator as well as the opposite indicator, each unit in a matched group will have the same CATE. For a unit $i$ in matched group $M$ of size $m$, the CATE of $i$ is thus estimated as: $$\frac{1}{m}\sum_{i:T_i=1}[\hat{Y}_i(1)]-\frac{1}{m}\sum_{i:T_i=0}[\hat{Y}_i(0)]$$



###### [](#header-6)Further Reference

For further reference on treatment effects, see [Imbens, Guido W. "Nonparametric estimation of average treatment effects under exogeneity: A review." ](https://www.mitpressjournals.org/doi/pdfplus/10.1162/003465304323023651?casa_token=fkH1Z_M2FG4AAAAA:MC8V9YAzYAn9YeT4cVvHQF0ZL12QsL8ZVFDX4juiQysLG5auaWyxdSzVrKINkH8nXwlN4P2r0wRq).




