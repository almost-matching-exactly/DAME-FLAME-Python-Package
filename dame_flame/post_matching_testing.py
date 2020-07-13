#%% Imports
import DAME_FLAME
import dame_flame
import pandas as pd
import time

#%% Speed test
df = pd.read_csv("data/10000x30.csv")

start0 = time.time()
result_new = DAME_FLAME.FLAME(input_data=df, verbose=0)
end0 = time.time()
print(end0 - start0)


start1 = time.time()
result_old = dame_flame.DAME_FLAME.FLAME(input_data=df, verbose=0)
end1 = time.time()
print(end1 - start1)
#%% MG comparison
mg_size = 4

start1 = time.time()
MMG_new = DAME_FLAME.MG(result, range(mg_size), df)
end1 = time.time()
duration1 = end1 - start1

start2 = time.time()
MMG_old = []
for i in range(mg_size):
    MMG_old.append(DAME_FLAME.mmg_of_unit(result_old,i,df))
end2 = time.time()
duration2 = end2 - start2

print('The new MG function was ' + str(round(duration2 / duration1,2)) + 
      ' times faster and took ' + str(round(duration1,2)) + ' seconds!')

#%% CATE comparison
cate_size = 4

start3 = time.time()
CATE_new = DAME_FLAME.CATE(result, range(cate_size), df)
end3 = time.time()
duration3 = end3 - start3

start4 = time.time()
CATE_old = []
for i in range(cate_size):
    CATE_old.append(DAME_FLAME.te_of_unit(result_old,i,df, 'treated','outcome'))
end4 = time.time()
duration4 = end4 - start4

print('The new CATE function was ' + str(round(duration4 / duration3,2)) + 
      ' times faster and took ' + str(round(duration3,2)) + ' seconds!')

#%% ATE and ATT
start5 = time.time()
ATE = DAME_FLAME.ATE(result,df)
end5 = time.time()

print('The ATE function took ' + str(round(end5 - start5,2)) + ' seconds!')

start6 = time.time()
ATT = DAME_FLAME.ATT(result,df)
end6 = time.time()

print('The ATT function took ' + str(round(end6 - start6,2)) + ' seconds!')