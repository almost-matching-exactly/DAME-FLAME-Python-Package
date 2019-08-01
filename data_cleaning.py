# -*- coding: utf-8 -*-
"""

@author: Neha
"""
import pandas as pd

def process_input_file(args):
    
    
    f = open(args.file_name[0], 'r')
    #for i in range(4):
    #    print(f.readline())
    
    df = pd.read_csv(args.file_name[0])
    print(df.head())
    
    # TODO: confirm that the treatment column name exists.
    
    # TODO: confirm that weight array has the right number of values in it
    
    # TODO: ensure that the columns are sorted in order: binary, tertary, etc
    
    return df, args.treatment_column_name[0]