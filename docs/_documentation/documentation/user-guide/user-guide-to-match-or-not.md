---
layout: default
title: Whether to use Matching
nav_order: 2
permalink: /documentation/user-guide/to-match-or-not
parent: User Guide
grand_parent: Documentation
has_children: true
---

# To Match or Not To Match
That is the question
{: .no_toc }

<details open markdown="block">
  <summary>
    Table of contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>


## Determining Whether to Use Matching Methods

Matching of treatment and control units can be a good method in order to determine treatment effects. However, certain criteria must be upheld in order for matching to be an appropriate solution for a given dataset. If these criteria are not upheld, perhaps other approaches to causal inference should be used in place of, or in addition to matching. 

### The Stable Unit Treatment Value Assumption (SUTVA)

Treatments applied to one unit should not affect the outcome of another unit. Units can not interfere with one another. This is reasonable in many situations: If two individuals are not in contact with each other, how would one individual taking a pain medication impact the outcome of another individual. 

We should also assume that the treatment doesn't have varying forms, and is completely binary. Individuals can not have taken pain medication of different strengths. 

### The Unconfoundedness Assumption

This is also referred to as "ignorability". It is important that the outcome is independent of the treatment when observable covaraiates are held constant. Omitted variable bias is a common issue that occurs when a variable impacts both treatment and outcomes, and appears in a bias of treatment effect estimates. 

In the example about pain medications, if a researcher fails to include in their dataset some underlying health condition that impacts response to pain medication, the impact of taking pain medication for a headache might be evaluated incorrectly.


### Overlap of Treatment and Control Groups

A common problem in causal inference is overlap or imbalance between treatment and control groups. A treatment and control group would have no overlap if none of the covariates have the same values. In this case, the FLAME and DAME algorithms would not find any matches, and no treatment effect estimates would be possible. 

A more moderate issue is partial overlap. In this case, some units do not have matches. Because the `DAME-FLAME` package allows for algorithm controls, even if all units could be matched in theory, users of the algorithm might prefer to avoid matching all units. Regardless of the cause, units that are unmatched do not have a CATE estimate, and they are not included in the treatment effect calculations either. 


## Additional Requirements For `DAME-FLAME`

Since `DAME-FLAME` is a package for matching treatment and control groups, we require all of the above criteria for users. 

Additionally, we impose one additional crucial requirement: that the datasets that contain discrete observational data. The outcome variable can be continuous, but we impose this requirement on all of the covariates. We do not recommend users bin continous covariates unless they are confident they are  in a way that is a typical, research driven separation. 

## Challenges in Matching Methods

"Exact matching" isn't possible when we a dataset has lots of characteristics about individuals, or is high dimensional. So, matching methods performing the best-possible alternative should be *interpretable*. Users of matching algorithms need to be able to easily understand which covariates were selected to be most important to their outcome, and need be able to find out why they were selected. This is important so that causal analysis can provide crucial information on who benefits from treatment most, where resources should be spent for future treatments, and why some individuals benefit from treatment while others were not. This can also help researchers determine what type of additional data must be collected. 

Secondly, the matches should also be *high quality*. If an oracle could tell us the exact result of doing treatment on any individual whose treatment we did not observe, then would we find that our estimate of the effect of treatment on that individual is accurate? 

###### [](#header-6)Further Reference

For further reference on causal inference research and its assumptions and issues, we recommend [Imbens, Guido W., and Donald B. Rubin. *Causal inference in statistics, social, and biomedical sciences.*](https://books.google.com/books?hl=en&lr=&id=Bf1tBwAAQBAJ&oi=fnd&pg=PR17&ots=jeVGafZSDE&sig=x9LYF4V9-wYQRQRxpudyA-d9nI0).

