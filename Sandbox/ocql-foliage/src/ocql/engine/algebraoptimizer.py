#
# Optimization will be done later,
# at the moment this is just a stub returning it's input
#
#

class EliminateMake:
    def __init__(self, algebra):
        self.algebra = algebra
    
    def applicable(self, alg):
        return isinstance(alg,self.algebra.Make) and \
            alg.coll1==alg.coll2 
    
    def __call__(self, alg):
        if self.applicable(alg):
            return alg.expr

class AlgebraOptimizer:
    def __init__(self, engine):
        self.engine = engine
    
    def optimize(self, alg):
        return alg

#        algebra = self.engine.algebra
#        return algebra.Iter(set,
#            algebra.If(algebra.Eq(algebra.Identifier('d.name'),algebra.Identifier('"Computing Science"')),
#                algebra.Select(set, algebra.Lambda('c',
#                    algebra.And(algebra.Reduce(set, algebra.Identifier('False'), 
#                               algebra.Lambda('d',algebra.Eq(algebra.Identifier('d'),algebra.Identifier('i'))), 
#                                      algebra.Identifier('or'), algebra.Identifier('c.runBy')),
#                        algebra.Le(algebra.Identifier('1'),algebra.Identifier('c.credits')),
#                        algebra.Le(algebra.Identifier('c.credits'),algebra.Identifier('3')))),
#                    algebra.Collection('ICurses')),
#                algebra.Empty(set,None)), 
#            algebra.Collection('IDepartments'))
