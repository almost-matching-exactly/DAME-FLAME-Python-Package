# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 14:46:49 2023

@author: Neha
"""
import pandas as pd
import numpy as np
import dame_flame

df = pd.DataFrame([[0,1,1,1,0,5.1], [np.nan,0,1,0,0,5.11], [1,0,1,1,1,6.5], 
                       [1,1,1,1,1,6.]],
                      columns=["x1", "x2", "x3", "x4", "treated", "outcome"])
model = dame_flame.matching.FLAME(verbose=3, missing_holdout_replace=2)
model.fit(df, "treated", "outcome")
result = model.predict(df, pre_dame=1)

print(result)
print(model.units_per_group)

mmg = dame_flame.utils.post_processing.MG(matching_object=model, unit_ids=2)
print("mmg", mmg)

cate = dame_flame.utils.post_processing.CATE(matching_object=model, unit_ids=0)
print("cate", round(cate,3))

ate = dame_flame.utils.post_processing.ATE(matching_object=model)
print("ate", round(ate,3))