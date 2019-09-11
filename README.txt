This package is not ready for deployment, it is still undergoing testing for correctness. 

Assumption/Bug warning: Currently, the computation for generating new active sets (I think) goes wrong if the column headers are longer
than 1 character, so just stick to column headers in the input file being '1', 'a', 'b', etc...for now. Sorry!

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
for each covariate set. It will be the length of the first item -1, so the 
0th index of this list will correspond to the 1st index of the 1st list, so
the PE of ['first variable'] is 1000. The 1st index of this list will 
correspond to the 2nd index of the first item, etc... 
Please note that this value will be bogus if the input parameter to DAME, adaptive_weights, is passed in as =True.
(sorry this is so confusing, Vittorio)

sample.csv is from the flame paper exactly
sample2.csv has one entry edited by me. 

Code organization:
Some test cases are in *_test.py
All 3 of the algorithms in the DAME paper are in dame_algorithms.py
The main starting point is DAME.py. 

Here's my remaining todo list (they're mostly commented in the code, but wanted to aggregate).

(Easy)
Author names in function headers, along with filling in the rest of them)
Need to add in the group by SQL implementation from Tianyu's code too
Allow for early stopping conditions based on weight or number of units being low
There might be a more time efficient implementation of checking for a single treatment unit remaining (checking Tianyu's code again)
Allow user to specify input algorithm type

(Harder)
More test cases 
A new structure for the output, involving two separate files/datasets listing groups and units. (Done, but confirm its as desired)
Allowing for CATE output values
Cynthia's experiments against the original DAME code (after next step)
Fix errors in my code of metric for match quality (imitated Jerry's code for this)

Main questions: Verification that the output options are formatted as desired.
Verification that quality metric should be Ridge Regression MSE regardless of algorithm used, or is that only for when the algorithm used is Ridge Reg MSE?
Is it always MSE?
Verification on correctness according to .csv test cases and the file called dame_algorithms_test.py
From the paper, it almost looks like there are 3 variations on this algorithm -- the one I did, the AME with fixed weights revisited, and full-ame with PE. 
I only have confirmed correctness on the first, looks like the code of Yameng does some 2nd/3rd hybrid...? It seems like true DYNAMIC-AME should have 3rd
only...