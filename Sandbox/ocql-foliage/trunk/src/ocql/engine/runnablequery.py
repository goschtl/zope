#
# Runnable query object
# This will return the resultset
#

_marker = object()

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
    def __init__(self, engine, alg, code):
        self.engine = engine
        self.alg = alg
        self.code =code
    
    def reanalyze(self):
        self.code = self.engine._compile_algebra(self.alg)
    
    def execute(self, debug=False):
        metadata = self.engine.metadata
        
        #return reduce(set.union, map(lambda c: reduce(set.union, map(lambda d: ((d.name=="Computing Science") and (((d==set(filter(lambda i: i.runBy,c))) and (((c.credits<=3) and (((1<=c.credits) and (set([c])) or (set()))) or (set()))) or (set()))) or (set())),set(metadata.getAll("IDepartments"))) , set()),set(metadata.getAll("ICurses"))) , set())
        
        #TODO: why is the metadata not working in locals?
        import operator
        
        mapping = {'metadata': self.engine.metadata,
                   'operator': operator}
        if debug:
            mapping['reduce'] = d_reduce
            mapping['map'] = d_map
            mapping['range'] = d_range
            mapping['set'] = d_set
        
        return eval(self.code, mapping, mapping)
        
        #return eval(self.code)
