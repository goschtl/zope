# -*- coding: UTF-8 -*-

"""Classes for the Query Object representation

$Id$
"""

#TODOS:
#move self.rewrite to ocql.rewriter into adapters

#add self.__repr__ to ALL, see Query class

#implement a traversable tree of queryobjects (parent, child, sibling, ....)

from zope.interface import implements
from zope.location import locate, Location
from zope.location.interfaces import ILocation

from ocql.interfaces import IObjectQuery
from ocql.interfaces import IObjectQueryHead
from ocql.queryobject.interfaces import *

class Head(Location):
    implements(IObjectQueryHead)
    def __init__(self, tree):
        self.name = 'head'
        self.tree = tree
        locate(tree, self, 'tree')

    def __repr__(self):
        return ('%s') % (self.tree) 

    def rewrite(self, algebra):
        return self.tree


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
                locate(term, self, 'term')
        self.children.extend(value)


class QueryObject(Child):
    #TODO: this is dirty here, at the end we'll need to have a tree of
    #QueryObject's whose topmost element will only get this IF
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

    def rewrite(self, algebra):
        raise NotImplementedError(self)

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
class hasClassWith(Expression):
    #NotImplementedError
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

#    def rewrite(self, algebra):
#        return algebra.Identifier(self.name)

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

#    def rewrite(self, algebra):
#        return algebra.Constant(self.value)

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

    def rewrite(self, algebra):
        self.symbols.addlevel()
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
                            self.symbols,
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
            elif isinstance(firstTerm, Alias):
                rv = Query(
                    self.metadata,
                    self.symbols,
                    self.collection_type,
                    [In(
                        self.metadata,
                        self.symbols,
                        firstTerm.identifier,
                        firstTerm.expression
                        )]+self.terms[1:],
                    self.target).rewrite(algebra)
            else:
                rv = algebra.If(
                    firstTerm.rewrite(algebra),
                    Query(
                        self.metadata,
                        self.symbols,
                        self.collection_type,
                        self.terms[1:],
                        self.target).rewrite(algebra),
                    algebra.Empty(self.collection_type, None)
                )
        else:
            rv = algebra.Single(
                self.collection_type,
                self.target.rewrite(algebra))

        self.symbols.dellevel()
        return rv

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

        s[self.identifier.name] = r

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

    def rewrite(self, algebra):
        return algebra.Binary(
            self.left.rewrite(algebra),
            self.get_operator(algebra),
            self.right.rewrite(algebra))

# Sets and properties
class Union(Binary):
    implements(IUnion)
    def rewrite(self, algebra):
        return algebra.Union(
            self.left.get_collection_type(),
            self.left.rewrite(algebra),
            self.right.rewrite(algebra))

class Differ(Binary):
    implements(IDiffer)
    def rewrite(self, algebra):
        return algebra.Differ(
            self.left.get_collection_type(),
            self.left.rewrite(algebra),
            self.right.rewrite(algebra))

class And(Binary):
    implements(IAnd)
    def get_operator(self, algebra):
        return algebra.Operator('and')

class Or(Binary):
    implements(IOr)
    def get_operator(self, algebra):
        return algebra.Operator('or')

class Property(Binary):
    implements(IProperty)
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

        #print self.left.name+'.'+self.right.name,r

        return r

class Index(Binary):
    #NotImplementedError
    implements(IIndex)


# Arithmetic operators
class Arithmetic(Binary):
    implements(IArithmetic)

class Add(Arithmetic):
    implements(IAdd)
    def get_operator(self, algebra):
        return algebra.Operator('+')

class Mul(Arithmetic):
    implements(IMul)
    def get_operator(self, algebra):
        return algebra.Operator('*')

class Sub(Arithmetic):
    implements(ISub)
    def get_operator(self, algebra):
        return algebra.Operator('-')

class Div(Arithmetic):
    implements(IDiv)
    def get_operator(self, algebra):
        return algebra.Operator('/')

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
    def rewrite(self, algebra):
        return algebra.Not(self.expression.rewrite(algebra))

class Aggregate(Unary):
    implements(IAggregate)


class Count(Aggregate):
    implements(ICount)
    def rewrite(self, algebra):
        return algebra.Reduce(
            bag, # FIXME milyen bag
            0,
            algebra.Lambda('i', algebra.Constant(1)),
            algebra.Operator('+'),
            make(bag, set, self.expression.rewrite(algebra))
            # FIXME ?set? must be determined by type(self.expression)
        )

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
        return "(%s)" % (
            self.__class__.__name__
            )

    def rewrite(self, algebra, expression, quanter, operator):
        raise NotImplementedError()

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

    def rewrite(self, algebra, expression, operator):
        return self.quantor.rewrite(algebra, expression, self.expression, operator)

# Quantors
class Every(Quantor):
    implements(IEvery)
    def rewrite(self, algebra, expression, quanted, operator):
        ctype = quanted.get_collection_type()

        return algebra.Reduce(
            ctype, # FIXME ?set? but which type() to take? quanted.expression?
            algebra.Identifier('True'),
            algebra.Lambda('i',
                operator.__class__(
                    self.metadata,
                    self.symbols,
                    Identifier(
                        self.metadata,
                        self.symbols,
                        'i'),
                    expression
                ).rewrite(algebra)
            ),
            algebra.Operator('and'),
            quanted.rewrite(algebra)
        )

class Some(Quantor):
    implements(ISome)
    def rewrite(self, algebra, expression, quanted, operator):
        ctype = quanted.get_collection_type()
        return algebra.Reduce(
            ctype, # FIXME ?set? but which type() to take? quanted.expression?
            algebra.Identifier('False'),
            algebra.Lambda('i',
                operator.__class__(
                    self.metadata,
                    self.symbols,
                    Identifier(self.metadata, self.symbols,'i'),
                    expression
                ).rewrite(algebra)
            ),
            algebra.Operator('or'),
            quanted.rewrite(algebra)
        )

class Atmost(Quantor):
    implements(IAtmost)
    #expr = None

    #def __init__(self, metadata, symbols, expr):
    #    raise NotImplementedError(self)
    #    self.metadata = metadata
    #    self.symbols = symbols
    #    self.expr = expr

class Atleast(Quantor):
    implements(IAtleast)
    #expr = None

    #def __init__(self, metadata, symbols, expr):
    #    raise NotImplementedError(self)
    #    self.metadata = metadata
    #    self.symbols = symbols
    #    self.expr = expr

class Just(Quantor):
    implements(IJust)
    #expr = None

    #def __init__(self, metadata, symbols, expr):
    #    raise NotImplementedError(self)
    #    self.metadata = metadata
    #    self.symbols = symbols
    #   self.expr = expr

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

    def rewrite(self, algebra):
        if isinstance(self.left, Quanted):
            return self.left.rewrite(
                algebra,
                self.right,
                self)
        if isinstance(self.right, Quanted):
            return self.right.rewrite(
                algebra,
                self.left,
                self)
        else:
            return algebra.Binary(self.left.rewrite(algebra), self.get_operator(algebra), self.right.rewrite(algebra))

class Eq(Condition):
    implements(IEq)
    def get_operator(self, algebra):
        return algebra.Operator('==')

class Ne(Condition):
    implements(INe)
    def get_operator(self, algebra):
        return algebra.Operator('!=')

class Lt(Condition):
    implements(ILt)
    def get_operator(self, algebra):
        return algebra.Operator('<')

class Gt(Condition):
    implements(IGt)
    def get_operator(self, algebra):
        return algebra.Operator('>')

class Le(Condition):
    implements(ILe)
    def get_operator(self, algebra):
        return algebra.Operator('<=')

class Ge(Condition):
    implements(IGe)
    def get_operator(self, algebra):
        return algebra.Operator('>=')

# TODO: missing:
    #xi{Es}
    #xi{E1..E2}
    #I(Es)
    #K
    #==,
    #~==
