# -*- coding: UTF-8 -*-

"""Runnable query object

Contains the runnable python code
This will return the resultset

$Id$
"""

import operator

from ocql.interfaces import IAlgebraOptimizer
from ocql.interfaces import IAlgebraCompiler
from ocql.exceptions import ReanalyzeRequired

_marker = object()

#these are here helper functions to debug compiled code
#set breakpoints here
#feel free to add classes and methods to debug

def d_reduce(function, sequence, initializer=_marker):
    if initializer is _marker:
        rv = reduce(function, sequence)
    else:
        rv = reduce(function, sequence, initializer)
    return rv

def d_map(function, *sequences):
    #print "Mapping from", [i for i in sequences[0]]
    rv = map(function, *sequences)
    return rv

def d_range(start, stop):
    rv = range(start, stop)
    return rv

class d_set(set):
    def union(self, other):
        rv = set.union(self, other)
        return rv

    def __call__(self):
        rv = set.__call__(self)
        return rv

    def __init__(self, list=[]):
        #print "creating set with values", list
        rv = set.__init__(self, list)
        return rv



class RunnableQuery:
    """
        metadata: ocql.metadata instance
        alg: algebra object
    """
    def __init__(self, metadata, originalAlgebra, code):
        self.metadata = metadata
        self.alg = originalAlgebra
        self.code = code

    def __repr__(self):
        return "%s: %s" % (self.__class__.__name__,
                           self.code)

    def reanalyze(self):
        optimizedalgebra = IAlgebraOptimizer(self.alg)(self.metadata)
        runnable = IAlgebraCompiler(optimizedalgebra)(self.metadata, optimizedalgebra)

        self.metadata = runnable.metadata
        self.alg = runnable.alg
        self.code = runnable.code

        return self

    def execute(self, debug=False, noretry=False):
        #TODO: why is the metadata not working in locals?

        mapping = {'metadata': self.metadata,
                   'operator': operator}
        if debug:
            mapping['reduce'] = d_reduce
            mapping['map'] = d_map
            mapping['range'] = d_range
            mapping['set'] = d_set

        try:
            return eval(self.code, mapping, mapping)
        except ReanalyzeRequired:
            if noretry:
                raise
            self.reanalyze()
            return eval(self.code, mapping, mapping)
