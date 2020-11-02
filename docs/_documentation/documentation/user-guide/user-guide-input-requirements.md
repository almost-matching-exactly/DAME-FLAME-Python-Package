---
layout: default
title: Discrete Observation Requirement
nav_order: 3
permalink: /documentation/user-guide/data-requirements
parent: User Guide
grand_parent: Documentation
has_children: true
---

# DAME-FLAME data requirements
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


## Discrete Observation Requirement for DAME-FLAME

The main requirements for researchers to justify the use of matching methods also hold for DAME-FLAME. Those are discussed [here](https://almost-matching-exactly.github.io/DAME-FLAME-Python-Package/documentation/user-guide/to-match-or-not). In sum, we require SUTVA, ignorability, and some overlap. 

Additionally, we require that all observational covariates be discrete. The outcome data can be continuous. The treatment indicator column must be binary. 

We **do not** recommend users bin continous covariates.

The only exception that could be made is a scenario where users are confident they are binning variables in a way that is a typical for their research. In this scenario, categories must be pre-defined and considered acceptable in their domain of work. 

### Example of Acceptable Binning

In research incorporating infant births, gestation time could be binned and used in `DAME-FLAME` as an observational covariate. Classifications of gestational age are well established norms adhered to in obstetric publications.  *Early term* is considered 37 0/7 weeks of gestation through 38 6/7 weeks of gestation, *full term*  is 39 0/7 weeks of gestation through 40 6/7 weeks of gestation, etc. The American College of Obstetricians and Gynecologists and the Society for Maternal-Fetal Medicine endorse and encourage these categories.

###### Reference
[ACOG Committee Opinion No 579: definition of term pregnancy](https://journals.lww.com/greenjournal/Fulltext/2013/11000/Committee_Opinion_No_579___Definition_of_Term.39.aspx)

### Input Format Example

Below, we provide an example of the format that the `DAME-FLAME` package requires input data to be in. The input data can be either a file, or a **Python Pandas Data Frame**. All covariates in the input data should be categorical covariates. If there are continuous covariates, we only recommend users regroup the data if they are sure they are doing so in a way that is typical of their research question. In addition to input observational data columns, the input data must contain (1) A column indicating the outcome variable as an *integer* or *float* data type, and (2) A column specifying whether a unit is treated or control (treated = 1, control = 0) as an *integer* data type. There are no requirements for input data column names or order of columns. Below is an example of input data with n units and m covariates.


*Column-name / unit-id*  | x_1 | x_2 |...| x_m | outcome | treated
--- | --- | --- | --- | --- | --- | --- |
**1** | 2 | 3 | ... | 4 | 9 | 0
**2** | 1 | 3 | ... | 3 | 5.5 | 1
**3** | 1 | 4 | ... | 5 | -1 | 0
... | ... | ... | ... | ... | ... | ...
**n** | 0 | 5 | ... | 0 | 1 | 1
*Data Type*| *integer* | *integer* | *integer* | *integer* |  *numeric* | *0 or 1* |

The holdout training set, if provided, should also follow the same format.

