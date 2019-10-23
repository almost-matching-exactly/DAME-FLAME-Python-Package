This package is not ready for deployment, it is still undergoing testing for correctness. 

Sample command:
x = DAME(file_name='sample2.csv', treatment_column_name='treated', outcome_column_name='outcome', 
adaptive_weights=True, holdout_file_name='sample2.csv', ate=False, repeats=False)

Output of the above command:
x = 
u first variable second variable
1              1               1
3              1               1
0              1               *
2              1               *

mmg_of_unit(x, 1, 'sample2.csv')

u first variable  second variable
1               1                1
3               1                1


Code organization:
Some test cases are in *_test.py
The main starting point is DAME.py. After cleaning, then it goes to dame_algorithm.py, which starts off the algorithm, and this calls other files. 

Here's my remaining todo list:

(harder/Questions):
1. How to transition from FLAME to DAME?

(Easy)
2. Allow for users to enter option for possible early stopping conditions based on weight or number of units being low
3. Allow user to input alpha options for decision trees
4. Need to fix up ATE to work with the new output format