#
# Algebra operators
#
from ocql.engine.algebra import Algebra

class BaseAlgebra(Algebra):
    pass

class Empty(BaseAlgebra):
    """
    >>> Empty(set,None).compile()
    'set()'
    >>> Empty(list,None).compile()
    '[]'
    """
    def __init__(self, klass, expr):
        self.klass = klass

    def compile(self):
        if self.klass==set:
            return 'set()'
        elif self.klass==list:
            return '[]'

    def __repr__(self):
        return 'Empty(%s)'%(self.klass)
    
    def walk(self):
        yield self
    
class Single(BaseAlgebra):
    """
    >>> Single(set,Constant('c')).compile()
    'set(c)'
    >>> Single(list,Constant('c')).compile()
    '[c]'
    """

    def __init__(self, klass, expr):
        self.klass = klass
        self.expr = expr

    def compile(self):
        if self.klass==set:
            return 'set(['+self.expr.compile()+'])'
        elif self.klass==list:
            return '['+self.expr.compile()+']'

    def __repr__(self):
        return 'Single(%s,%s)'%(self.klass,self.expr)

    def walk(self):
        yield self
        for t in self.expr.walk():
            yield t
    
class Union(BaseAlgebra):
    """
    >>> Union(set,Empty(set,None),Single(set,Identifier('c'))).compile()
    'set.union(set(),set(c))'
    >>> Union(list,Empty(list,None),Single(list,Identifier('c'))).compile()
    '([])+([c])'
    """
    def __init__(self, klass, coll1, coll2):
        self.klass=klass
        self.coll1=coll1
        self.coll2=coll2

    def compile(self):
        if self.klass==set:
            return 'set.union(%s,%s)' % (self.coll1.compile(),self.coll2.compile())
        elif self.klass==list:
            return '(%s)+(%s)'%(self.coll1.compile(),self.coll2.compile())

    def __repr__(self):
        return 'Union(%s,%s,%s)'%(self.klass,self.coll1,self.coll2)

    def walk(self):
        yield self
        for t in self.coll1.walk():
            yield t
        for t in self.coll2.walk():
            yield t

class Iter(BaseAlgebra):
    def __init__(self, klass, func, coll):
        self.klass = klass
        self.func = func
        self.coll = coll

    def compile(self):
        if self.func is Lambda and \
                self.coll is Collection and \
                self.func.expr is If:
            
            # You can place here some specialized code...
            if self.klass == set:
                return 'reduce(set.union, map(%s,%s) , set())' % \
                    (self.func.compile(),self.coll.compile())
            if self.klass == list:
                return 'reduce(operator.add, map(%s,%s) , [])' % \
                    (self.func.compile(),self.coll.compile())
        else:
            if self.klass == set:
                return 'reduce(set.union, map(%s,%s) , set())' % \
                    (self.func.compile(),self.coll.compile())
            if self.klass == list:
                return 'reduce(operator.add, map(%s,%s) , [])' % \
                    (self.func.compile(),self.coll.compile())

    def __repr__(self):
        return "Iter(%s,%s,%s)"%(self.klass,self.func,self.coll)

    def walk(self):
        yield self
        for t in self.func.walk():
            yield t
        for t in self.coll.walk():
            yield t
    
class Select(BaseAlgebra):
    def __init__(self, klass, func, coll):
        self.klass = klass
        self.func = func
        self.coll = coll

    def compile(self):
        if self.klass == set:
            return 'set(filter(%s,%s))' % (self.func.compile(),self.coll.compile())
        if self.klass == list:
            return 'filter(%s,%s)' % (self.func.compile(),self.coll.compile())

    def __repr__(self):
        return "Select(%s,%s,%s)"%(self.klass,self.func,self.coll)

    def walk(self):
        yield self
        for t in self.func.walk():
            yield t
        for t in self.coll.walk():
            yield t
        
class Reduce(BaseAlgebra):
    def __init__(self, klass, expr, func, aggreg, coll):
        self.klass = klass
        self.expr = expr
        self.func = func
        self.aggreg = aggreg
        self.coll = coll

    def compile(self):
        if self.klass == set:
            #adi: [] needed, otherwise iteration over non-seq
            return 'set(filter(%s,[%s]))' % (self.func.compile(),self.coll.compile())
        if self.klass == list:
            return 'filter(%s,[%s])' % (self.func.compile(),self.coll.compile())

    def __repr__(self):
        return "Reduce(%s,%s,%s,%s,%s)"%(self.klass,self.expr,self.func,self.aggreg,self.coll)

    def walk(self):
        yield self
        for t in self.expr.walk():
            yield t
        for t in self.func.walk():
            yield t
        for t in self.aggreg.walk():
            yield t
        for t in self.coll.walk():
            yield t

#class Equal:
#    def __init__(self, klass, coll1, coll2):
#        self.klass = klass
#        self.coll1 = coll1
#        self.coll2 = coll2
#    
#    def compile(self):
#        if self.klass == set:
#            return 'set(filter(%s,%s))' % (self.coll1.compile(),self.coll1.compile())
#        if self.klass == list:
#            return 'filter(%s,%s)' % (self.coll1.compile(),self.coll2.compile())
#
#class Differ:
#    def __init__(self, klass, start, enf):
#        self.klass = klass
#        self.start = start
#        self.end = end
#    
#    def compile(self):
#        if self.klass == set:
#            return 'set(range(%s,%s))' % (self.start.compile(),self.end.compile())
#        if self.klass == list:
#            return 'range(%s,%s)' % (self.start.compile(),self.end.compile())
        
class Range(BaseAlgebra):
    def __init__(self, klass, start, enf):
        self.klass = klass
        self.start = start
        self.end = end
    
    def compile(self):
        if self.klass == set:
            return 'set(range(%s,%s))' % (self.start.compile(),self.end.compile())
        if self.klass == list:
            return 'range(%s,%s)' % (self.start.compile(),self.end.compile())
        
    def walk(self):
        yield self
        for t in self.start.walk():
            yield t
        for t in self.end.walk():
            yield t
    

#class Index

class Make(BaseAlgebra):
    def __init__(self, coll1, coll2, expr):
        self.expr = expr
        self.coll1 = coll1
        self.coll2 = coll2

    def compile(self):
        return '%s(metadata.getAll("%s"))' % (self.coll1.__name__,self.expr.compile())
    
    def __repr__(self):
        return "Make(%s,%s,%s)" %(self.coll1,self.coll2,self.expr)

    def walk(self):
        yield self
        for t in self.expr.walk():
            yield t
    
#class And:
#class Being:

class If(BaseAlgebra):
    def __init__(self, cond, expr1, expr2):
        self.cond = cond
        self.expr1 = expr1
        self.expr2 = expr2
    
    def compile(self):
        return '((%s) and (%s) or (%s))' % (self.cond.compile(),self.expr1.compile(),self.expr2.compile())
    
    def __repr__(self):
        return "If(%s,%s,%s)" % (self.cond,self.expr1,self.expr2)

    def walk(self):
        yield self
        for t in self.cond.walk():
            yield t
        for t in self.expr1.walk():
            yield t
        for t in self.expr2.walk():
            yield t

#
# 
#
class Lambda(BaseAlgebra):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

    def compile(self):
        return 'lambda %s: %s'%(self.var,self.expr.compile())

    def __repr__(self):
        return "Lambda %s: %s" %(self.var,self.expr)

    def walk(self):
        yield self
        for t in self.expr.walk():
            yield t
        
class Constant(BaseAlgebra):
    def __init__(self, value):
        self.value = value

    def compile(self):
        return '%s'%(self.value)

    def __repr__(self):
        return "`%s`" %(self.value)

    def walk(self):
        yield self
    
class Identifier(BaseAlgebra):
    def __init__(self, name):
        self.name=name
    
    def compile(self):
        return self.name
    
    def __repr__(self):
        return "%s" % self.name

    def walk(self):
        yield self
    
class Binary(BaseAlgebra):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def compile(self):
        return '%s%s%s' % (self.left.compile(),self.op.compile(),self.right.compile())

    def __repr__(self):
        return "%s%s%s" % (self.left,self.op.compile(),self.right)

    def walk(self):
        yield self
        for t in self.left.walk():
            yield t
        for t in self.right.walk():
            yield t
    
class Operator(BaseAlgebra):
    def __init__(self,op):
        self.op = op
        
    def compile(self):
        return self.op
    
    def __repr__(self):
        return self.op

    def walk(self):
        yield self
#class Property:
#   def __init__(self, left, right):
#        self.left = left
#        self.right = right
#    
#    def compile(self):
#        return '%s.%s' (self.left.compile(),self.right.compile())
#    
#    def __repr__(self):
#        return '%s.%s' (self.left,self.right)

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()

