This package is NOT user friendly yet. 

Assuming no repeat column headers/all unique, ordered from least to greatest number of bits.

Sample command if using Spyder on Windows:
$ runfile('DAME.py', "--valid_group_by bit-vector --file_name sample.csv --treatment_column_name T --weight_array '0.75, 0.25'")
If using any other command line I think (sorry, haven't confirmed yet) this should be:
$ python3 DAME.py --valid_group_by bit-vector --file_name sample.csv --treatment_column_name T --weight_array '0.55, 0.25'


sample.csv is from the flame paper exactly
sample2.csv has one entry edited by me. 

Code organization:
Some test cases are in *_test.py
All 3 of the algorithms in the DAME paper are in dame_algorithms.py
The main starting point is DAME.py. 

Here's my remaining todo list (they're mostly commented in the code, but wanted to aggregate).

(Easy)
I mistakenly thought we wanted variables named according to the paper and will change those. (So "lambda" will become "active_covariates", etc. Whoops!)
Author names in function headers, along with filling in the rest of them)
Validate user input (weight vector correct length? Adds to one? Included treatment column? Column headers unique? etc)
Need to add in the group by SQL implementation from Tianyu's code too
Allow for early stopping conditions based on weight or number of units being low
There might be a more time efficient implementation of checking for a single treatment unit remaining (checking Tianyu's code again)

(Harder)
More test cases
a new structure for the output, involving two separate files/datasets listing groups and units. Also, allowing for CATE output values