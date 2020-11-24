---
layout: default
title: Natality Experiment 
nav_order: 5
permalink: /examples/natality_experiment/
parent: Examples
---

# Experiment on Natality Dataset
{: .fs-9 }

In the linked Github file, we aim to examine the effect of "extreme smoking" of a mother during pregancy on her newborn's birthweight. Overall, the results of the DAME-FLAME package lead us to believe that smoking during pregnancy causes significantly lower birthweight of infants. It also leads us to believe that there is little to no heterogeneity in conditional treatment effects of a mother's smoking on birthweight. In other words, when we examine groupings of characteristics of mothers and infants (including race, gender of infant, etc), then we don't see evidence that there exists some mothers and infants for whom the impact of maternal smoking on infant birthweight is different than the outcomes for other types of mothers and infants.

We use the 2010 US Natality dataset from the <a href="#references">National Vital Statistics System of the National Center for Health Statistics (2010)</a>.  The accompanying user guide to the dataset is also linked with that URL, labelled "documentation".

Similar analysis is done in <a href="#references">Wang, et al (2020)</a>. Notable differences between the two are that this experiment uses a smaller dataset and a slightly modified algorithm. This experiment aims to build upon the analysis on maternal smoking and infant birthweight shown in <a href="#references"> Kondracki (2020)</a>. 

Four key takeaways from the experiment on github:
1. A common question about the `dame-flame` package is the discrete observational data requirement. This experiment uses data that is discrete, such as day of week, and total birth order. It also uses data that is binned continuous data, such as father's age, which has been binned into fixed width intervals of five year age groups (15-19 years, 20-24 years, etc.). Mother's education is also binned into bins with the completion of a degree, not the number of days of school attended. Both of these variables are binned in a way that is commonly done within research using this dataset, or similar datasets. 

 2. The covariate dropping order, shown above using the `verbose=3` parameter, is something we use to interpret covariate importance. The FLAME algorithm learns the importance of each covariate on the outcome when choosing the best covariate to drop. Thus, the earlier dropped covariates can be considered less relevant to the outcome. In this case, FLAME would lead us to believe that some factors, such as mother's education and the day of the week of the infant birth, are less predictive of an infant's birth weight than other factors, such as the sex of the infant.

3. The ATE is highly negative. This leads us to believe that maternal extreme smoking causes an infant's birthweight to be lower than not smoking by several grams.

4. Lastly, the plot as shown below, of CATE of matched groups against matched group size, leads us to believe there is little heterogeneity in the Conditional Average Treatment Effect (CATE) of maternal smoking on infant birth weight. Most extreme values are observed in small matched groups, for which CATE estimation is difficult. Put simply, we don't see evidence that there exists some "types of" mothers and infants (classified by characteristics such as education and race) for whom the impact of maternal smoking on infant birthweight is different than the outcomes for other mothers and infants.


![Graph](https://raw.githubusercontent.com/nehargupta/dame-flame-experiments/master/Natality_Dataset_CATE_mgs.png "Graph")

[Download Example From GitHub](https://raw.githack.com/nehargupta/dame-flame-experiments/master/Natality_Experiment.html){: .btn .btn-primary .fs-4 .mb-4 .mb-md-0 }


<div id="references" class="language-markdown highlighter-rouge">
  <h4>References</h4>
    <a class="number" href="#exact-matching">[1]</a> 
    <a href="http://www2.nber.org/data/vital-statistics-natality-data.html">
    NCHS' Vital Statistics Natality Birth Data.
  </a>
  <br>
  <a class="number" href="#exact-matching">[2]</a> 
    <a href="https://arxiv.org/abs/1707.06315">
    Wang, Morucci, et al. <i>FLAME: A Fast Large-scale Almost Matching Exactly Approach to Causal Inference</i>.
  </a>
  <br>
  <a class="number" href="#exact-matching">[3]</a> 
    <a href="https://link.springer.com/content/pdf/10.1186/s12884-020-02981-1.pdf">
    Kondracki, Anthony J. "Low birthweight in term singletons mediates the association between maternal smoking intensity exposure status and immediate neonatal intensive care unit admission: the E-value assessment."<i> BMC Pregnancy and Childbirth </i>20 (2020): 1-9..
  </a>
</div>


{: .fs-6 .fw-300 }
