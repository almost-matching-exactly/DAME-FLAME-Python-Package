This package is not ready for deployment, it is still undergoing testing for correctness. 

Assumption/Bug warning: Currently, the computation for generating new active sets (I think) goes wrong if the column headers are longer
than 1 character, so just stick to column headers in the input file being '1', 'a', 'b', etc... until I've confirmed the fix. Sorry!

Sample command if using Spyder on Windows:
$ runfile('DAME.py', "--valid_group_by bit-vector --file_name sample.csv --treatment_column_name T --weight_array '0.75, 0.25'")
If using any other command line I think (sorry, haven't confirmed yet) this should be:
$ python3 DAME.py --valid_group_by bit-vector --file_name sample.csv --treatment_column_name T --weight_array '0.55, 0.25'

Sample command from inline in Python code:
DAME(valid_group_by='bit-vector', file_name = 'sample.csv', \
         treatment_column_name = 'treated', weight_array = [0.75, 0.25],
	adaptive_weights=True)



Output interpretation of the above command:
([['first variable', 'second variable'], ['first variable']],
 [[1, 1, '*'], [1, '*', '*']],
 [(1, 0), (3, 0), (1, 1), (2, 1), (3, 1)],
 [1000])

The first item [['first variable', 'second variable'], ['first variable']] indicates which covariates were used in the match
So we know that in the first match, we used covariates ['first variable', 'second variable'], and in the second match.
we used the covariate set ['first variable']

The second item, [[1, 1, '*'], [1, '*', '*']], indicates what each group looks like.
So we know that in the 0th group, the pairs had values [1, 1, '*'], and in the 1st group, the pairs had values [[1, '*', '*']]

The third item,  [(1, 0), (3, 0), (1, 1), (2, 1), (3, 1)]), indicates what entry is in each group. 
So we know that unit 1 and 3 are in the 0th group, and unit 1,2, and 3 are in the 1st group. 

The last item, [1000] is a list of PE, where PE=(MSE treated + MSE control)
for each covariate set if If adaptive_weights=True, and based on running ridge reg with alpha = 0.1 to decide which covar to drop.
Or, if adaptive_weights=False, then it reports the weighted sum of weights. 
0th index of this list will correspond to the 1st index of the 1st list, so
the PE of ['first variable'] is 1000. The 1st index of this list will 
correspond to the 2nd index of the first item, etc... 

Code organization:
Some test cases are in *_test.py
The main starting point is DAME.py. After cleaning, then it goes to dame_algorithm.py, which starts off the algorithm, and this calls other files. 

Here's my remaining todo list (they're mostly commented in the code, but wanted to aggregate).

(Easy)
Author names in function headers, along with filling in the rest of them
Need to add in the group by SQL implementation from Tianyu's code too
Allow for early stopping conditions based on weight or number of units being low
There might be a more time efficient implementation of checking for a single treatment unit remaining (check Tianyu's code again)
Allow user to input alpha options for ridge reg

(Harder)
More test cases 
A new structure for the output, involving two separate files/datasets listing groups and units. (Done, but confirm its as desired)
Allowing for CATE output values
Support ATE and ATT output. 
experiments against the original DAME code (after next step) -- this looks hard because I don't know how they generated their data 
Support for more algorithms than just fixed weight linear reg and adaptive weight ridge. 

Main questions: Verification that the output options are formatted as desired.
Verification on correctness according to .csv test cases and the file called dame_algorithms_test.py
Do we care about weight^2 variation?