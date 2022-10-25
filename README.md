[![Build Status](https://app.travis-ci.com/almost-matching-exactly/DAME-FLAME-Python-Package.svg?branch=master)](https://app.travis-ci.com/almost-matching-exactly/DAME-FLAME-Python-Package)
[![Coverage Status](https://coveralls.io/repos/github/almost-matching-exactly/DAME-FLAME-Python-Package/badge.svg)](https://coveralls.io/github/almost-matching-exactly/DAME-FLAME-Python-Package)

<!-- Comment hi.  -->
# DAME-FLAME
A Python package for performing matching for observational causal inference on datasets containing discrete covariates
--------------------------------------------------

## Documentation [here](https://almost-matching-exactly.github.io/DAME-FLAME-Python-Package/)

DAME-FLAME is a Python package for performing matching for observational causal inference on datasets containing discrete covariates. It implements the Dynamic Almost Matching Exactly (DAME) and Fast, Large-Scale Almost Matching Exactly (FLAME) algorithms, which match treatment and control units on subsets of the covariates. The resulting matched groups are interpretable, because the matches are made on covariates, and high-quality, because machine learning is used to determine which covariates are important to match on.

### Installation

#### Dependencies
`dame-flame` requires Python version (>=3.6.5). Install from [here](https://www.python.org/downloads/) if needed.

- pandas>=0.11.0
- numpy>= 1.16.5
- scikit-learn>=0.23.2


If your python version does not have these packages, install from [here](https://packaging.python.org/tutorials/installing-packages/).

To run the examples in the examples folder (these are not part of the package), Jupyter Notebooks or Jupyter Lab (available [here](https://jupyter.org/install)) and Matplotlib (>=2.0.0) is also required.

#### User Installation

Download from PyPi via
$ pip install dame-flame


# A Tutorial to FLAME-database version

#### Make toy dataset 
```
import pandas as pd
from dame_flame.flame_db.utils import *
from dame_flame.flame_db.FLAME_db_algorithm import *

train_df = pd.DataFrame([[0,1,1,1,0,5], [0,1,1,0,0,6], [1,0,1,1,1,7], [1,1,1,1,1,7]], 
                  columns=["x1", "x2", "x3", "x4", "treated", "outcome"])
test_df = pd.DataFrame([[0,1,1,1,0,5], [0,1,1,0,0,6], [1,0,1,1,1,7], [1,1,1,1,1,7]], 
                  columns=["x1", "x2", "x3", "x4", "treated", "outcome"])                 
```

#### Connect to the database
```
select_db = "postgreSQL"  # Select the database you are using: "MySQL", "postgreSQL","Microsoft SQL server"
database_name='tmp' # database name you use 
host = 'localhost' 
port = "5432"
user="postgres"
password= ""

conn = connect_db(database_name, user, password, host, port)
```



#### Insert the data to be matched into database

If you already have the dataset in the database, please ignore this step. Insert the test_df (data to be matched) into the database you are using.
```
from dame_flame.flame_db.gen_insert_data import *
insert_data_to_db("datasetToBeMatched", # The name of your table containing the dataset to be matched
                  test_df,
                  treatment_column_name= "treated",
                  outcome_column_name= 'outcome',conn = conn)
```
#### Run FLAME_db

```
res = FLAME_db(input_data = "datasetToBeMatched", # The name of your table containing the dataset to be matched
              holdout_data = train_df, # holdout set. We will use holdout set to train our model
              conn = conn # connector object that connects to your database. This is the output from function connect_db.
              )
```

#### Analysis results
```
res[0]:
    data frame of matched groups. Each row represent one matched groups.
    res[0]['avg_outcome_control']: 
        average of control units' outcomes in each matched group   
    res[0]['avg_outcome_treated']: 
        average of treated units' outcomes in each matched group   
    res[0]['num_control']:
        the number of control units in each matched group
    res[0]['num_treated']:
        the number of treated units in each matched group
    res[0]['is_matched']:
        the level each matched group belongs to
res[1]:
    a list of level numbers where we have matched groups
res[2]:
    a list of covariate names that we dropped
```
#### Postprocessing

```
ATE_db(res) # Get ATE for the whole dataset
ATT_db(res) # Get ATT for the whole dataset
```
