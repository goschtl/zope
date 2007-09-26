#
# Classes for the Query Object representation
#

class NotImplemented(Exception):
    pass

class QueryObject:
    metadata = None
    
    def __init__(self, metadata):
        self.metadata = metadata
        
    def addSymbol(self):
        pass
        
    def get_class(self):
        s = self.metadata.symbols.current()
        try:
            return s[self.name]
        except KeyError:
            return self.metadata.get_class(self.name)
        except AttributeError:
            from pub.dbgpclient import brk; brk()

    
    def get_collection_type(self, klass=None):
        if klass is None:
            klass = self.get_class()
            
            if klass is None:
                from pub.dbgpclient import brk; brk()

        rv = klass.get_collection_type()
        print self.name,rv
        return rv

    def rewrite(self, algebra):
        raise NotImplemented(self) 

class Term:
    pass
        
class Expression(Term, QueryObject):
    pass

#
# General
# 
class hasClassWith(Expression):
    #NotImplemented
    expression = None
    klass = None
    conditional = None
    
    def __init__(self, metadata, expr, klass, conditional):
        self.metadata = metadata
        self.expression = expression
        self.klass = klass
        self.conditional = conditional

class Identifier(Expression):
    name = None
    
    def __init__(self, metadata, name):
        self.metadata = metadata
        self.name = name

    def rewrite(self, algebra):
        return algebra.Identifier(self.name)

class Constant(Expression):
    #this shall be abstract?
    value = None
    
    def __init__(self, metadata, value):
        self.metadata = metadata
        self.value=value
    
    def rewrite(self, algebra):
        return algebra.Constant(self.value)

class StringConstant(Constant):
    pass

class NumericConstant(Constant):
    #TODO: convert value to string?
    pass

class BooleanConstant(Constant):
    #TODO: convert value to string?
    pass

class CollectionConstant(Constant):
    pass
   
class Query(Expression):
    collection_type = None
    terms = None
    target = None
        
    def __init__(self, metadata, collection_type, terms, target):
        self.metadata = metadata
        self.collection_type = collection_type
        self.terms = terms
        self.target = target
    
    def get_collection_type(self, klass=None):
        return self.collection_type
    
    def rewrite(self, algebra):
        self.metadata.symbols.addlevel()
        rv=None
        
        if len(self.terms):
            for t in self.terms:
                t.addSymbol()
            
            firstTerm = self.terms[0]
            if isinstance(firstTerm, In):
                
                ctype = firstTerm.get_collection_type()
                
                rv = algebra.Iter(
                    self.collection_type,
                    algebra.Lambda(
                        firstTerm.identifier.name,
                        Query(
                            self.metadata,
                            self.collection_type,
                            self.terms[1:],
                            self.target
                            ).rewrite(algebra)
                    ), algebra.Make(
                        self.collection_type,
                        ctype,
                        firstTerm.expression.rewrite(algebra)
                        ) # FIXME: ?set? must be determined by type(firstTerm.expression)
                )
            elif isinstance(firstTerm,Alias):
                rv = Query(
                    self.metadata,
                    self.collection_type,
                    [In(
                        self.metadata,
                        firstTerm.identifier,
                        firstTerm.expression
                        )]+self.terms[1:], 
                    self.target).rewrite(algebra)
            else:
                rv = algebra.If(
                    firstTerm.rewrite(algebra),
                    Query(
                        self.metadata,
                        self.collection_type,
                        self.terms[1:],
                        self.target).rewrite(algebra),
                    algebra.Empty(self.collection_type, None)
                )
        else:
            rv = algebra.Single(
                self.collection_type,
                self.target.rewrite(algebra))
        
        self.metadata.symbols.dellevel()
        return rv

class In(Term):
    identifier = None
    expression = None
        
    def __init__(self, metadata, identifier, expression):
        self.metadata = metadata
        self.identifier = identifier
        self.expression = expression
    
    def addSymbol(self):
        s = self.metadata.symbols.current()
        #s[self.identifier.name] = self.metadata.get_class(
        #    self.expression.name)
        s[self.identifier.name] = self.expression.get_class()
    
    def get_collection_type(self):
        rv = self.expression.get_collection_type()
        return rv

class Alias(Term):
    identifier = None
    expression = None
    
    def __init__(self, metadata, identifier, expression):
        self.metadata = metadata
        self.identifier = identifier
        self.expression = expression
    
    def addSymbol(self):
        s = self.metadata.symbols.current()
        #TODO: that's not really good
        r = self.expression.get_collection_type()
        
        s[self.identifier.name] = r
    
    def get_collection_type(self):
        rv = self.expression.get_collection_type()
        print self.expression.name,rv
        return rv

#
# Binary operators
#
class Binary(Expression):
    left = None
    right = None
        
    def __init__(self, metadata, left, right):
        self.metadata = metadata
        self.left = left
        self.right = right

    def rewrite(self, algebra):
        return algebra.Binary(
            self.left.rewrite(algebra),
            self.get_operator(algebra),
            self.right.rewrite(algebra))

# Sets and properties
class Union(Binary):
    def rewrite(self, algebra):
        algebra.Union(
            left.rewrite(algebra),
            right.rewrite(algebra))

class Differ(Binary):
    def rewrite(self, algebra):
        algebra.Differ(
            left.rewrite(algebra),
            right.rewrite(algebra))

class And(Binary):
    def get_operator(self, algebra):
        return algebra.Operator('and')

class Or(Binary):
    def get_operator(self, algebra):
        return algebra.Operator('or')

class Property(Binary):
    def rewrite(self, algebra): # FIXME: Ezt gondold at...
        return algebra.Identifier(
            '.'.join([self.left.name, self.right.name]))
    
    def get_class(self):
        t = self.left.get_class()
        
        return t
    
    def get_collection_type(self):
        t = self.left.get_class()
        try:
            r = t[self.right.name]
        except:
            from pub.dbgpclient import brk; brk()

        print self.left.name+'.'+self.right.name,r
        
        return r

class Index(Binary):
    #NotImplemented
    pass


# Arithmetic operators
class Arithmetic(Binary):
    pass

class Add(Arithmetic):
    def get_operator(self,algebra):
        return algebra.Operator('+')

class Mul(Arithmetic):
    def get_operator(self,algebra):
        return algebra.Operator('*')

class Sub(Arithmetic):
    def get_operator(self,algebra):
        return algebra.Operator('-')

class Div(Arithmetic):
    def get_operator(self,algebra):
        return algebra.Operator('/')

#
# Unary operators
#
class Unary(Expression):
    expression = None
    
    def __init__(self, metadata, expression):
        self.metadata = metadata
        self.expression = expression

class Not(Unary):
    def rewrite(self, algebra):
        return algebra.Not(self.expression.rewrite(algebra))

class Aggregate(Unary):
    pass

class Count(Aggregate):
    def rewrite(self, algebra):
        return algebra.Reduce(
            bag, # FIXME milyen bag
            0,
            algebra.Lambda('i',algebra.Constant(1)),
            algebra.Operator('+'), 
            make(bag,set,self.expression.rewrite(algebra))
            # FIXME ?set? must be determined by type(self.expression)
        )

class Sum(Aggregate):
    #NotImplemented
    pass

#
# Conditional
#
class Quantor(QueryObject):
    def rewrite(self, algebra, expression, quanter, operator):
        raise NotImplemented()

class Quanted:
    quantor = None
    expression = None
    
    def __init__(self, metadata, quantor, expression):
        self.metadata = metadata
        self.quantor = quantor
        self.expression = expression
    
    def rewrite(self, algebra, expression, operator):
        return self.quantor.rewrite(algebra, expression, self.expression, operator)

# Quantors
class Every(Quantor):
    def rewrite(self, algebra, expression, quanted, operator):
        ctype = quanted.get_collection_type()
        
        return algebra.Reduce(
            ctype, # FIXME ?set? but which type() to take? quanted.expression?
            algebra.Identifier('True'),
            algebra.Lambda('i',
                operator.__class__(
                    self.metadata,
                    Identifier(
                        self.metadata,
                        'i'),
                    expression
                ).rewrite(algebra)
            ),
            algebra.Operator('and'),
            quanted.rewrite(algebra)
        )

class Some(Quantor):
    def rewrite(self, algebra, expression, quanted, operator):
        ctype = quanted.get_collection_type()
        return algebra.Reduce(
            ctype, # FIXME ?set? but which type() to take? quanted.expression?
            algebra.Identifier('False'),
            algebra.Lambda('i',
                operator.__class__(
                    self.metadata,
                    Identifier(self.metadata, 'i'),
                    expression
                ).rewrite(algebra)
            ),
            algebra.Operator('or'),
            quanted.rewrite(algebra)
        )

class Atmost(Quantor):
    expr = None
    
    def __init__(self, metadata, expr):
        raise NotImplemented(self)
        self.metadata = metadata
        self.expr = expr

class Atleast(Quantor):
    expr = None
    
    def __init__(self, metadata, expr):
        raise NotImplemented(self)
        self.metadata = metadata
        self.expr = expr

class Just(Quantor):
    expr = None
    
    def __init__(self, metadata, expr):
        raise NotImplemented(self)
        self.metadata = metadata
        self.expr = expr

# Logical operators
class Condition(Expression):
    left = None
    right = None
        
    def __init__(self, metadata, left, right):
        self.metadata = metadata
        self.left = left
        self.right = right

    def rewrite(self, algebra):
        if isinstance(self.left,Quanted):
            return self.left.rewrite(
                algebra,
                self.right,
                self)
        if isinstance(self.right,Quanted):
            return self.right.rewrite(
                algebra,
                self.left,
                self)
        else:
            return algebra.Binary(self.left.rewrite(algebra),self.get_operator(algebra),self.right.rewrite(algebra))

class Eq(Condition):
    def get_operator(self,algebra):
        return algebra.Operator('==')

class Ne(Condition):
    def get_operator(self,algebra):
        return algebra.Operator('!=')

class Lt(Condition):
    def get_operator(self,algebra):
        return algebra.Operator('<')

class Gt(Condition):
    def get_operator(self,algebra):
        return algebra.Operator('>')

class Le(Condition):
    def get_operator(self,algebra):
        return algebra.Operator('<=')

class Ge(Condition):
    def get_operator(self,algebra):
        return algebra.Operator('>=')

# TODO: missing:
    #xi{Es}
    #xi{E1..E2}
    #I(Es)
    #K
    #==,
    #~==
