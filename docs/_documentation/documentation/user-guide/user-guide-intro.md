---
layout: default
title: Introduction to Causal Inference
nav_order: 1
permalink: /documentation/user-guide/Introduction
parent: User Guide
grand_parent: Documentation
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

## Introduction to Causal Inference

Causal inference is the attempt to draw conclusions that *something* is being caused by *something else*. It goes beyond questions of correlation, association, and is distinct from model-based predictive analysis. Questions of robust causal inference are practically unavoidable in health, medicine, or social studies. 

Much of the available data in the clinical and social sciences is *observational*, and we can only observe one outcome per individual. For example, if one individual took pain reliever for a headache and they now feel better, we don't know what would have happened to that same individual over the same time period, if they had not taken pain reliever. Taking the pain reliever puts them in the *treatment* group, but since we don't know what the *control* outcome of not taking pain reliever would be (without time travel), how can we say pain reliever *caused* the headache to go away? 

## Introduction to Matching

When estimating causal effects in an observational setting, one common approach is to *match* each treatment unit to an identical control unit. Going back to the example, can we find two people sharing every physical attribute, who also had the exact same symptoms, prior to the time when only one of them taking the pain reliever? Secondly, how did their outcomes differ? 

In large datasets where we observe many characteristics about individuals, few "identical twins", (referred to as "exact matches") exist. What is the best way to match individuals that were treated and controlled? Only once they're matched are we able to apply common *treatment effect estimators* to the groups of matched individuals, in order to try to determine the effect of treatment.

<div class="language-markdown highlighter-rouge">
  <h4>Further Readings</h4>
  <br/>
  For more information on causal inference research and its assumptions and issues, we recommend
  <a href="https://books.google.com/books?hl=en&lr=&id=Bf1tBwAAQBAJ&oi=fnd&pg=PR17&ots=jeVGafZSDE&sig=x9LYF4V9-wYQRQRxpudyA-d9nI0">
    Imbens, Guido W., and Donald B. Rubin. <i>Causal inference in statistics, social, and biomedical sciences</i>.
  </a>
</div>

