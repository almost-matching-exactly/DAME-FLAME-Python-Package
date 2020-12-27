# -*- coding: utf-8 -*-
"""Algorithm to generate sets in "Dynamic Almost Matching" (Liu, et al)"""

# author: Neha Gupta, Duke University
# Copyright Duke University 2020
# License: MIT

import itertools

def algo3GenerateNewActiveSets(newly_dropped, prev_processed):
    """This function does Algorithm 3 in the paper.

    Args:
        newly_dropped: A newly dropped set of size k. Stored as type frozenset.
            This is s in the paper.
        prev_processed: the set of previously processed sets. Stored as set of
            frozensets. This is delta in the paper.

    Returns:
        Z, the new active sets. Stored as set of frozensets.

    """
    new_active_sets = set() # this is Z in the paper
    size_newly_dropped = len(list(newly_dropped)) # this is k in the paper
    set_newly_dropped = set(newly_dropped)

    # Step 3: delta_k is a set of frozensets.
    # it contains all subsets of delta that are size k, and s.
    subsets_size_k = set()
    for fs_prevprocessed in prev_processed:
        if len(fs_prevprocessed) == size_newly_dropped:
            subsets_size_k.add(fs_prevprocessed)
    subsets_size_k.add(newly_dropped)
    delta_k = subsets_size_k

    # Step 4: rho is all the covariates contained in sets in delta_k
    rho = set()
    for tup in delta_k:
        for i in tup:
            rho.add(i)

    # Step 5: s_e is the support of covariate e in delta_k, for covars in rho
    # possible time efficiency exploration: combine this with above loop, 
    # calculating rho in one step
    s_e = dict()
    for covar_e in rho:
        s_e[covar_e] = 0
        for tup in delta_k:
            if covar_e in tup:
                s_e[covar_e] += 1

    # Step 6: omega is all the covariates not in s that have enough support
    # .items() iterates through key,val pairs
    # so dict_covars_eno is the dictionary of all covariates that have enough support
    dict_covars_eno = dict((key, val) for key, val in s_e.items() if val >= size_newly_dropped)
    omega = set(dict_covars_eno.keys())
    omega = omega.difference(set_newly_dropped)


    # Step 7: do all covariates in S have enough support in delta_k?
    for covar_e, support_e in s_e.items():
        if covar_e in newly_dropped and support_e < size_newly_dropped:
            return new_active_sets

    # Step 8
    for alpha in omega:
        # Step 9
        r = set_newly_dropped.union(set([alpha]))

        # Step 10: Get all subsets of size_newly_dropped in r, check if belong in delta_k

        # Have to convert these to sets and frozen sets before doing the search
        delta_k = set(frozenset(i) for i in delta_k)
        subsets_size_k = set(list(itertools.combinations(r, size_newly_dropped)))
        subsets_size_k = set(frozenset(i) for i in subsets_size_k)

        allin = True
        for subset in subsets_size_k:
            if subset not in delta_k:
                allin = False
                break

        if allin:
            # Step 11: Add r to Z
            new_active_sets.add(frozenset(r))

    return new_active_sets
