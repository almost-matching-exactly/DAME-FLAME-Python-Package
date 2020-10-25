---
layout: default
title: Introduction
nav_order: 1
permalink: /documentation/user-guide/Introduction
parent: User Guide
grand_parent: Documentation
has_children: true
---

# Introduction
{: .no_toc }

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## Introduction to Causal Inference and Matching

Causal inference is the attempt to draw conclusions that *something* is being caused by *something else*. It goes beyond questions of correlation, association, and is distinct from model-based predictive analysis. Questions of robust causal inference are practically unavoidable in health, medicine, or social studies. 

Much of the available data in the clinical and social sciences is *observational*, and we can only observe one outcome per individual. For example, if one individual took pain reliever for a headache and they now feel better, we don't know what would have happened to that same individual over the same time period, if they had not taken pain reliever. Taking the pain reliever puts them in the *treatment* group, but since we don't know what the *control* outcome of not taking pain reliever would be (without time travel), how can we say pain reliever *caused* the headache to go away? 

When estimating causal effects in an observational setting, one common approach is to *match* each treatment unit to an identical control unit. Going back to the example, can we find two people sharing every physical attribute, who also had the exact same symptoms, prior to the time when only one of them taking the pain reliever? Secondly, how did their outcomes differ? 

In large datasets where we observe many characteristics about individuals, few "identical twins", (referred to as "exact matches") exist. What is the best way to match individuals that were treated and controlled? Only once they're matched are we able to apply common *treatment effect estimators* to the groups of matched individuals, in order to try to determine the effect of treatment.


## Determining Whether to Use Matching Methods

Matching of treatment and control units can be a good method in order to determine treatment effects. However, certain criteria must be upheld in order for matching to be an appropriate solution for a given dataset. If these criteria are not upheld, perhaps matching should be used in addition to other approaches for causal inference. 

### The Stable Unit Treatment Value Assumption (SUTVA)

Treatments applied to one unit should not affect the outcome of another unit. Units can not interfere with one another. This is reasonable in many situations: If two individuals are not in contact with each other, how would one individual taking a pain medication impact the outcome of another individual. 

We should also assume that the treatment doesn't have varying forms, and is completely binary. Individuals can not have taken pain medication of different strengths. 

### The Unconfoundedness Assumption

This is also referred to as "ignorability". It is importat that the outcome is independent of the treatment when observable covaraiates are held constant. Omitted variable bias is a common issue that occurs when a variable impacts both treatment and outcomes, and appears in a bias of treatment effect estimates. 

In the example about pain medications, if a researher fails to include in their dataset some underlying health condition that impacts response to pain medication, the impact of taking pain medication for a headache might be evaluated incorrectly.

### Additional Requirements For `DAME-FLAME`

As a final note, `DAME-FLAME` is intended for use on datasets that contain discrete covariates. We provide some examples and discuss the importance of the discrete datasets in (link) and (link). 


## Challenges in Matching Methods

"Exact matching" isn't possible when we a dataset has lots of characteristics about individuals, or is high dimensional. So, matching methods performing the best-possible alternative should be *interpretable*. Users of matching algorithms need to be able to easily understand which covariates were selected to be most important to their outcome, and need be able to find out why they were selected. This is important so that causal analysis can provide crucial information on who benefits from treatment most, where resources should be spent for future treatments, and why some individuals benefit from treatment while others were not. This can also help researchers determine what type of additional data must be collected. Interpretability of the matches provided by `DAME-FLAME` is discussed in (link). 

Secondly, the matches should also be *high quality*. If an oracle could tell us the exact result of doing treatment on any individual whose treatment we did not observe, then would we find that our estimate of the effect of treatment on that individual is accurate? Determining the treatment effect of a match is discussed in (link). 

###### [](#header-6)Further Reference

For further reference on causal inference research and its assumptions and issues, we recommend [Imbens, Guido W., and Donald B. Rubin. *Causal inference in statistics, social, and biomedical sciences.*](https://books.google.com/books?hl=en&lr=&id=Bf1tBwAAQBAJ&oi=fnd&pg=PR17&ots=jeVGafZSDE&sig=x9LYF4V9-wYQRQRxpudyA-d9nI0).

