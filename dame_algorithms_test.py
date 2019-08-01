# -*- coding: utf-8 -*-
"""
@author: Neha
"""
import dame_algorithms
import unittest
import pandas as pd

class TestAlgorithm3(unittest.TestCase):

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
    

if __name__ == '__main__':
    unittest.main()