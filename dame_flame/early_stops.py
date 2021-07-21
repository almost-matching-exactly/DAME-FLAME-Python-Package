# -*- coding: utf-8 -*-
"""For organizing all of the early stopping criteria options"""
# author: Neha Gupta, Duke University
# Copyright Duke University 2020
# License: MIT

class EarlyStops:
    '''
    Class to hold all early stopping criteria as decided by user
    '''
    def __init__(self):
        '''
        Constructor, defaults all of the possible early stopping criteria
        '''
        # create the members
        self.unmatched_c = False
        self.unmatched_t = False
        self.un_c_frac = 0.1
        self.un_t_frac = 0.1
        self.pe = 0.05
        self.iterations = False
