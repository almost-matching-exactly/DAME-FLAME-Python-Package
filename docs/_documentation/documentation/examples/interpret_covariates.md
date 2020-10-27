---
layout: default
title: Interpreting Covariate Importance

nav_order: 4
permalink: /examples/interpretability/
parent: Examples
---

# Interpreting Covariate Importance
{: .fs-9 }

We say that this is an *interpretable* matching package because it will allow users to quickly and easily understand which covariates were selected to be important to their outcome. 

This can be useful in determining who benefits from treatment the most and where resources should be spent for future treatment. 

In this example, using the ``verbose==3`` option, we show how to view the iterations of the algorithm and infer the best covariates. We begin with a simulated dataset in which five covariates are labelled 0 to 4, and the covariates are of exponentially decreasing importance to the outcome as the label  numberincreases.  

We see from the output that the FLAME algorithm drops unimportant covariates earlier in its algorithm. A user who did not have knowledge of the data generating process could interpret from the output of FLAME that the covariates dropped were of lower importance than the covariates matched on. 

<div class="early_stop" markdown="1">
```python

import dame_flame
df,_ = dame_flame.utils.data.gen_data_decay_importance(num_control=50, num_treated=50, num_cov=5,
                                                       bernoulli_param=0.5, bi_mean=2, bi_stdev=1)

model = dame_flame.matching.FLAME(verbose=3, want_pe=True, want_bf=True)
model.fit(holdout_data=df)
res = model.predict(df)
```
</div>

![interpretability verbose](https://github.com/nehargupta/dame-flame-experiments/raw/master/verbose_interpretability.PNG "interpretability")

[Download Example From GitHub](https://github.com/nehargupta/dame-flame-experiments/blob/master/interpretability.ipynb){: .btn .fs-5 .mb-4 .mb-md-0 }


{: .fs-6 .fw-300 }
