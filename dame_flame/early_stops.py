# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 19:24:34 2020

@author: Neha
"""

class EarlyStops:
    def __init__(self):
        ''' Constructor, defines all of the possible early stops needed '''
        # create the members
        self.unmatched_c = False
        self.unmatched_t = False
        self.un_c_frac = 0.1
        self.un_t_frac = 0.1
        self.pe = 0.1
        self.bf = 0.1
        self.iterations = False