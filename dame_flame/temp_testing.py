#%% Imports
import DAME_FLAME
import pandas as pd

#%% Test
df = pd.read_csv("data/data.csv")
result_new = DAME_FLAME.FLAME(input_data=df,verbose=0,repeats = False)

#%% Post-matching functions
print(DAME_FLAME.MG(result_new, [0,14], df))   
print(DAME_FLAME.CATE(result_new, [0,14], df))
print(DAME_FLAME.ATE(result_new, df))
print(DAME_FLAME.ATT(result_new, df))
