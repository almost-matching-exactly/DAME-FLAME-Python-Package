This package is not ready for deployment, it is still undergoing testing for correctness. 

Sample commands:
x = DAME(file_name='sample5.csv', treatment_column_name='treated', outcome_column_name='outcome', 
adaptive_weights='ridge', holdout_file_name='sample5.csv', repeats=True, want_pe=False)


Output of the above command:
x =    
   1  2  3
1  0  1  *
2  0  1  *
0  1  1  *
3  1  1  *
4  1  1  *

mmg_of_unit(x, 1, 'sample2.csv')

u first variable  second variable
1               1                1
3               1                1

x,y = FLAME(file_name='sample5.csv', treatment_column_name='treated', outcome_column_name='outcome', 
adaptive_weights='ridge', holdout_file_name='sample5.csv', repeats=True, pre_dame=1)

output:
x = empty dataframe
y =
   1  3
1  0  *
2  0  *
0  1  *
3  1  *
4  1  *

Code organization:
Some test cases are in *_test.py
The main starting point is DAME.py. After cleaning, then it goes to dame_algorithm.py, which starts off the algorithm, and this calls other files. 

Here's my remaining todo list:


(Easy)
2. Allow for users to enter option for possible early stopping conditions based on weight or number of units being low
3. Allow user to input alpha options for decision trees
