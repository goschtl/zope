#
# Runnable query object
# This will return the resultset
#

#import __builtin__

_marker = object()

def d_reduce(function, sequence, initializer=_marker):
    if initializer is _marker:
        rv = reduce(function, sequence)
    else:
        rv = reduce(function, sequence, initializer)
    return rv
    

class RunnableQuery:
    """
        metadata: ocql.metadata instance
        alg: algebra object
    """
    def __init__(self, engine, alg):
        self.engine = engine
        self.alg = alg
        self.reanalyze()
    
    def reanalyze(self):
        self.code = self.engine.compile_algebra(self.alg)
    
    def execute(self, debug=False):
        metadata = self.engine.metadata
        
        #return reduce(set.union, map(lambda c: reduce(set.union, map(lambda d: ((d.name=="Computing Science") and (((d==set(filter(lambda i: i.runBy,c))) and (((c.credits<=3) and (((1<=c.credits) and (set([c])) or (set()))) or (set()))) or (set()))) or (set())),set(metadata.getAll("IDepartments"))) , set()),set(metadata.getAll("ICurses"))) , set())
        
        #TODO: why is the metadata not working in locals?
        import operator
        
        mapping = {'metadata': self.engine.metadata,
                   'operator': operator}
        if debug:
            mapping['reduce'] = d_reduce
        
        return eval(self.code, mapping, mapping)
        
        #return eval(self.code)
