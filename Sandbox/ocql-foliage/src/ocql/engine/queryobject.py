#
# Classes for the Query Object representation
#

class NotImplemented(Exception):
    pass

class QueryObject:
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
    def __init__(self, expr, klass, conditional):
        self.expression = expression
        self.klass = klass
        self.conditional = conditional

class Identifier(Expression):
    def __init__(self, name):
        self.name = name

    def rewrite(self, algebra):
        return algebra.Identifier(self.name)

class Constant(Expression):
    #this shall be abstract?
    def __init__(self, value):
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
   
class Query(Expression):
    def __init__(self, collection, terms, target):
        self.collection = collection
        self.terms = terms
        self.target = target
    
    def rewrite(self, algebra):
        if len(self.terms):
            ft = self.terms[0]
            if isinstance(ft,In):
                return algebra.Iter(
                    self.collection,
                    algebra.Lambda(
                        ft.identifier.name,
                        Query(
                            self.collection,
                            self.terms[1:],
                            self.target
                            ).rewrite(algebra)
                    ), algebra.Make(
                        self.collection,
                        set,
                        ft.expression.rewrite(algebra)
                        ) # FIXME: ?set? 
                )
            elif isinstance(ft,Alias):
                return Query(
                    self.collection,
                    [In(ft.identifier,ft.expression)]+self.terms[1:], 
                    self.target).rewrite(algebra)
            else:
                return algebra.If(
                    ft.rewrite(algebra),
                    Query(
                        self.collection,
                        self.terms[1:],
                        self.target).rewrite(algebra),
                    algebra.Empty(self.collection, None)
                )
        else:
            return algebra.Single(
                self.collection,
                self.target.rewrite(algebra))

class In(Term):
    def __init__(self, identifier, expression):
        raise NotImplemented()
        self.identifier = identifier
        self.expression = expression

class Alias(Term):
    def __init__(self, identifier, expression):
        raise NotImplemented()
        self.identifier = identifier
        self.expression = expression

#
# Binary operators
#
class Binary(Expression):
    def __init__(self, left, right):
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
    def __init__(self, expression):
        self.expression = expression

class Not(Unary):
    def rewrite(self, algebra):
        return algebra.Not(self.expression.rewrite(algebra))

class Aggregate(Unary):
    pass

class Count(Aggregate):
    def rewrite(self, algebra):
        return algebra.reduce(
            bag, # FIXME milyen bag
            0,
            algebra.Lambda('i',algebra.Constant(1)),
            algebra.Operator('+'), 
            make(bag,set,self.expression.rewrite(algebra)) # FIXME ?set?
        )

class Sum(Aggregate):
    #NotImplemented
    pass

#
# Conditional
#
class Quantor:
    def rewrite(self, algebra, expression, quanter, operator):
        raise NotImplemented()

class Quanted:
    def __init__(self, quantor, expression):
        self.quantor = quantor
        self.expression = expression
    
    def rewrite(self, algebra, expression, operator):
        return self.quantor.rewrite(algebra, expression, self.expression, operator)

# Quantors
class Every(Quantor):
    #NotImplemented
    pass

class Some(Quantor):
    def rewrite(self, algebra, expression, quanted, operator):
        return algebra.Reduce(
            set, # FIXME ?set?
            algebra.Identifier('False'),
            algebra.Lambda('i',
                operator.__class__(
                    Identifier('i'),
                    expression
                ).rewrite(algebra)
            ),
            algebra.Operator('or'),
            quanted.rewrite(algebra)
        )

class Atmost(Quantor):
    def __init__(self, expr):
        raise NotImplemented(self) 
        self.expr = expr

class Atleast(Quantor):
    def __init__(self, expr):
        raise NotImplemented(self) 
        self.expr = expr

class Just(Quantor):
    def __init__(self, expr):
        raise NotImplemented(self) 
        self.expr = expr

# Logical operators
class Condition(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def rewrite(self, algebra):
        if isinstance(self.left,Quanted):
            return self.left.rewrite(algebra, self.right, self)
        if isinstance(self.right,Quanted):
            return self.right.rewrite(algebra, self.left, self)
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

# TODO: missing xi{Es} xi{E1..E2} I(Es) K ==, ~==
