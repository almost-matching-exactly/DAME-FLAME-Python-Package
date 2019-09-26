# -*- coding: utf-8 -*-
"""
@author: Neha
"""
import generate_new_active_sets
import unittest
import pandas as pd

class TestAlgorithm3(unittest.TestCase):
    ''' This tests just algorithm 3 in the paper, the find new active set part.
    Uses the example from the paper but with variations on data type just
    to make sure its robust to that
    '''
    
    def test_paper_example(self):
        s = frozenset((2, 3))
        delta = {frozenset((1,)), frozenset((1,2)), \
                 frozenset((1,3)), frozenset((1,5)), \
                 frozenset((2,)), frozenset((3,)), frozenset((5,))}
        omega = {frozenset((1, 2, 3))}
        self.assertEqual(algo3GenerateNewActiveSets(s,delta), omega)
    
    '''
    def test_paper_example(self):
        s = {(2, 3)}
        delta = {(1,), (1, 2), (1, 3), (1, 5), (2,), (3,), (5,)}
        omega = {frozenset((1, 2, 3))}
        self.assertEqual(algo3GenerateNewActiveSets(s,delta), omega)
    
    
    def test_paper_example_str(self):
        s = {('second', 'third')}
        delta = {('first',), ('first', 'second'), ('first', 'third'), ('first', 'fifth'), ('second',), ('third',), ('fifth',)}
        omega = {frozenset(('first', 'second', 'third'))}
        self.assertEqual(algo3GenerateNewActiveSets(s,delta), omega)
        
    def test_paper_example_frozensets(self):
        s = {frozenset(('second', 'third'))}
        delta = {frozenset(('first',)), frozenset(('first', 'second')), \
                 frozenset(('first', 'third')), frozenset(('first', 'fifth')), \
                 frozenset(('second',)), frozenset(('third',)), frozenset(('fifth',))}
        omega = {frozenset(('first', 'second', 'third'))}
        self.assertEqual(algo3GenerateNewActiveSets(s,delta), omega)
   ''' 

if __name__ == '__main__':
    unittest.main()