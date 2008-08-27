# -*- coding: UTF-8 -*-

"""Classes for the Query Object representation

$Id$
"""

#TODOS:

# TODO: missing:
#xi{Es}
#xi{E1..E2}
#I(Es)
#K
#==,
#~==

from zope.interface import implements
from zope.location import locate, Location
from zope.location.interfaces import ILocation

from ocql.interfaces import IObjectQuery
from ocql.interfaces import IObjectQueryHead
from ocql.queryobject.interfaces import *

class Head(Location):
    implements(IObjectQueryHead)
    def __init__(self, tree):
        self.__name__ = 'head'
        self.tree = tree
        locate(tree, self, 'tree')

    def __repr__(self):
        return ('Head(%s)') % (self.tree)

class Child(Location):
    implements(IObjectQueryChild)

    def __init__(self):
        self.children = []

    def setProp(self, name, value):
        setattr(self, name, value)
        if ILocation.providedBy(value):
            locate(value, self, name)
            self.children.append(value)

    def setProperties(self, name, value):
        setattr(self, name, value)
        for term in value:
            if ILocation.providedBy(term):
                locate(term, self, name)
        self.children.extend(value)

class QueryObject(Child):
    implements(IObjectQuery)

    metadata = None
    symbols = None

    def __init__(self, metadata, symbols):
        self.metadata = metadata
        self.symbols = symbols

    def addSymbol(self):
        pass

    def get_class(self):
        s = self.symbols.current()
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
        #print self.name,rv
        return rv

class Term(Child):
    implements(ITerm)
    identifier = None
    expression = None

    def __init__(self, metadata, symbols, identifier, expression):
        self.metadata = metadata
        self.symbols = symbols
        Child.__init__(self)
        self.setProp('identifier', identifier)
        self.setProp('expression', expression)

class Expression(Term, QueryObject):
    implements(IExpression)

#
# General
#
class Isinstance(Expression):
    implements(IIsinstance)

    def __init__(self, metadata, symbols, objekt, tipe):
        self.metadata = metadata
        self.symbols = symbols
        Child.__init__(self)
        self.setProp('objekt', objekt)
        self.setProp('tipe', tipe)

    def __repr__(self):
        return "%s(%s, %s)" % (
            self.__class__.__name__,
            str(self.objekt),
            str(self.tipe)
            )


class hasClassWith(Expression):
    implements(IhasClassWith)

    expression = None
    klass = None
    conditional = None

    def __init__(self, metadata, symbols, expr, klass, conditional):
        self.metadata = metadata
        self.symbols = symbols
        Child.__init__(self)
        self.setProp('expr', expr)
        self.setProp('klass', klass)
        self.setProp('conditional', conditional)

class Identifier(Expression):
    implements(IIdentifier)
    name = None

    def __init__(self, metadata, symbols, name):
        self.metadata = metadata
        self.symbols = symbols
        Child.__init__(self)
        self.setProp('name', name)

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            str(self.name),
            )

class Constant(Expression):
    implements(IConstant)
    #this shall be abstract?
    value = None

    def __init__(self, metadata, symbols, value):
        self.metadata = metadata
        self.symbols = symbols
        Child.__init__(self)
        self.setProp('value', value)

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__, self.value)

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
    implements(IQuery)
    collection_type = None
    terms = None
    target = None

    def __init__(self, metadata, symbols, collection_type, terms, target):
        self.metadata = metadata
        self.symbols = symbols
        Child.__init__(self)
        self.setProp('collection_type', collection_type)
        self.setProperties('terms', terms)
        self.setProp('target', target)

    def __repr__(self):
        return "%s(%s, %s, %s)" % (
            self.__class__.__name__,
            str(self.collection_type),
            '; '.join([str(t) for t in self.terms]),
            str(self.target)
        )

    def get_collection_type(self, klass=None):
        return self.collection_type

class In(Term):
    implements(IIn)
    def __repr__(self):
        return "%s(%s, %s)" % (
            self.__class__.__name__,
            str(self.identifier),
            str(self.expression)
            )

    def addSymbol(self):
        s = self.symbols.current()
        #s[self.identifier.name] = self.metadata.get_class(
        #    self.expression.name)
        s[self.identifier.name] = self.expression.get_class()

    def get_collection_type(self):
        rv = self.expression.get_collection_type()
        return rv

class Alias(Term):
    implements(IAlias)
    def __repr__(self):
        return "%s(%s, %s)" % (
            self.__class__.__name__,
            str(self.identifier),
            str(self.expression)
            )

    def addSymbol(self):
        s = self.symbols.current()
        #TODO: that's not really good
        r = self.expression.get_collection_type()

        s[self.identifier] = r

    def get_collection_type(self):
        rv = self.expression.get_collection_type()
        #print self.expression.name,rv
        return rv

#
# Binary operators
#
class Binary(Expression):
    implements(IBinary)
    left = None
    right = None

    def __init__(self, metadata, symbols, left, right):
        self.metadata = metadata
        self.symbols = symbols
        Child.__init__(self)
        self.setProp('left', left)
        self.setProp('right', right)

    def __repr__(self):
        return "%s(%s, %s)" % (
            self.__class__.__name__,
            str(self.left), str(self.right)
            )

# Sets and properties
class Union(Binary):
    implements(IUnion)

class Differ(Binary):
    implements(IDiffer)

class And(Binary):
    implements(IAnd)

class Or(Binary):
    implements(IOr)

class Property(Binary):
    implements(IProperty)

    def get_class(self):
        t = self.left.get_class()
        return t

    def get_collection_type(self):
        t = self.left.get_class()
        if IIdentifier.providedBy(self.right):
            try:
                r = t[self.right.name]
            except:
                from pub.dbgpclient import brk; brk()
        #print self.left.name+'.'+self.right.name,r
        else:
            try:
                r = t[self.right.left.name]
            except:
                from pub.dbgpclient import brk; brk()

        return r

        #else:
         #   return self.right.get_collection_type()

class Index(Binary):
    #NotImplementedError
    implements(IIndex)

# Arithmetic operators
class Arithmetic(Binary):
    implements(IArithmetic)

class Add(Arithmetic):
    implements(IAdd)

class Mul(Arithmetic):
    implements(IMul)

class Sub(Arithmetic):
    implements(ISub)

class Div(Arithmetic):
    implements(IDiv)

#
# Unary operators
#
class Unary(Expression):
    implements(IUnary)
    expression = None

    def __init__(self, metadata, symbols, expression):
        self.metadata = metadata
        self.symbols = symbols
        Child.__init__(self)
        self.setProp('expression', expression)

    def __repr__(self):
        return "%s(%s)" % (
            self.__class__.__name__,
            str(self.expression)
            )

class Not(Unary):
    implements(INot)

class Aggregate(Unary):
    implements(IAggregate)

class Count(Aggregate):
    implements(ICount)

class Sum(Aggregate):
    #NotImplementedError
    implements(ISum)

#
# Conditional
#
class Quantor(QueryObject):
    implements(IQuantor)
    def __init__(self, metadata, symbols, expr):
        self.metadata = metadata
        self.symbols = symbols
        Child.__init__(self)
        self.setProp('expr', expr)

    def __repr__(self):
        return "(%s, %s)" % (
            self.__class__.__name__,
            str(self.expr)
            )

class Quanted(Child):
    implements(IQuanted)
    quantor = None
    expression = None

    def __init__(self, metadata, symbols, quantor, expression):
        self.metadata = metadata
        self.symbols = symbols
        Child.__init__(self)
        self.setProp('quantor', quantor)
        self.setProp('expression', expression)

    def __repr__(self):
        return "%s(%s, %s)" % (
            self.__class__.__name__,
            str(self.quantor), str(self.expression)
            )

# Quantors
class Every(Quantor):
    implements(IEvery)

class Some(Quantor):
    implements(ISome)

class Atmost(Quantor):
    implements(IAtmost)

class Atleast(Quantor):
    implements(IAtleast)

class Just(Quantor):
    implements(IJust)

# Logical operators
class Condition(Expression):
    implements(ICondition)
    left = None
    right = None

    def __init__(self, metadata, symbols, left, right):
        self.metadata = metadata
        self.symbols = symbols
        Child.__init__(self)
        self.setProp('left', left)
        self.setProp('right', right)

    def __repr__(self):
        return "%s(%s, %s)" % (
            self.__class__.__name__,
            str(self.left), str(self.right)
            )

class Eq(Condition):
    implements(IEq)

class Ne(Condition):
    implements(INe)

class Lt(Condition):
    implements(ILt)

class Gt(Condition):
    implements(IGt)

class Le(Condition):
    implements(ILe)

class Ge(Condition):
    implements(IGe)
