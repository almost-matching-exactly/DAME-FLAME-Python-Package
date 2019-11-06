This package is not ready for deployment, it is still undergoing testing for correctness. 

Sample commands:
x = DAME(file_name='sample5.csv', treatment_column_name='treated', outcome_column_name='outcome', 
adaptive_weights='ridge', holdout_file_name='sample5.csv', repeats=True, want_pe=False)

Arguments:
- file_name. CSV file. Must be discrete data. Must have a treatment column and a outcome column.
- treatment_column_name: The name of the treatment column in the above file name
- outcome_column_name: The name of the outcome column in the aboe file name
- weight_array (optional): array of weights of all covariates. Only needed if adaptive_weights = True.
- adaptive_weights: 3 options: False, 'ridge', or 'decision tree'
- holdout_file_name (optional). Also a csv file, must have the same treatment and outcome column as above. 
	If not provided (or False), and adaptive weights = True, will default to same as file_name.
- repeats: Bool, whether or not values for whom a MMG has been found can
            be used again and placed in an auxiliary matched group. Default is True.
- want_pe: bool, default is false. Whether or not we want predictive error of each match



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


userxtmp/user/
nohup command &
"no hangup" so exiting out of terminal keeps it running
command can be my start.py whihc has a main funciton and a datetime to run my python file. 
can print output to the file. 
request@cs.duke.edu
ssh to login@cs.duke.edu on mobaxterm
$ ssh linux
in login1@linux > cd /usr/xtmp/nrg18/

to copy files over from laptop to ssh dir, use mobaxterm on my personal laptop to go into the directory Duke and then do a command:
$ scp -r CynthiaResearch/ nrg18@login.cs.duke.edu:/usr/xtmp/nrg18


This command is behaing oddly:
x = DAME(file_name='old-dame-code-input-df.csv', treatment_column_name='treated', outcome_column_name='outcome', adaptive_weights='ridge', holdout_file_name='old-dame-code-input-holdout.csv', repeats=True, want_pe=False)

