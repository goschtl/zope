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
    
    def execute(self):
        metadata = self.engine.metadata
        
        #return reduce(set.union, map(lambda c: reduce(set.union, map(lambda d: ((d.name=="Computing Science") and (((d==set(filter(lambda i: i.runBy,c))) and (((c.credits<=3) and (((1<=c.credits) and (set([c])) or (set()))) or (set()))) or (set()))) or (set())),set(metadata.getAll("IDepartments"))) , set()),set(metadata.getAll("ICurses"))) , set())
        
        #return eval(self.code,
        #            {},
        #            {'metadata': self.engine.metadata})
        return eval(self.code)
