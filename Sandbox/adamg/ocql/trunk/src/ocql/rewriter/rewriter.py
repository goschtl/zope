# -*- coding: UTF-8 -*-

"""Rewrites the Query Object to Algebra Object

$Id$
"""

from zope.component import adapts
from zope.interface import implements
from zope.location import locate
from zope.component import provideAdapter

from ocql.interfaces import IRewriter
from ocql.interfaces import IOptimizedObjectQuery
from ocql.rewriter.algebra import *
from ocql.queryobject.interfaces import *
from ocql.rewriter import algebra as target_algebra
import ocql.queryobject.queryobject

class Rewriter(object):
    implements(IRewriter)
    adapts(IOptimizedObjectQuery)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        query = self.context.tree
        adapter = IRewriter(query)
        alg = adapter()
        return Head(alg)

class ChildRewriter(object):
    def __init__(self, context):
        self.context = context

class IdentifierRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IIdentifier)

    def __call__(self):
        return Identifier(self.context.name)

class ConstantRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IConstant)

    def __call__(self):
        return Constant(self.context.value)

class QueryRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IQuery)

    def __call__(self):
        self.context.symbols.addlevel()
        rv=None

        if len(self.context.terms):
            for t in self.context.terms:
                t.addSymbol()

            firstTerm = self.context.terms[0]
            if isinstance(firstTerm, ocql.queryobject.queryobject.In):

                ctype = firstTerm.get_collection_type()

                rv = Iter(
                        self.context.collection_type,
                        Lambda(
                            firstTerm.identifier.name,
                            IRewriter(ocql.queryobject.queryobject.Query(
                                self.context.metadata,
                                self.context.symbols,
                                self.context.collection_type,
                                self.context.terms[1:],
                                self.context.target
                                ))()
                        ), Make(
                            self.context.collection_type,
                            ctype,
                            IRewriter(firstTerm.expression)()
                            ) # FIXME: ?set? must be determined by type(firstTerm.expression)
                )
            elif isinstance(firstTerm, ocql.queryobject.queryobject.Alias):
                rv = Iter(
                        self.context.collection_type,
                        Lambda(IRewriter(firstTerm.identifier)(),
                               Single(self.context.collection_type, IRewriter(firstTerm.identifier)())),
                        Single(self.context.collection_type, IRewriter(firstTerm.expression)()))

            else:
                rv = If(
                    IRewriter(firstTerm)(),
                    IRewriter(ocql.queryobject.queryobject.Query(
                        self.context.metadata,
                        self.context.symbols,
                        self.context.collection_type,
                        self.context.terms[1:],
                        self.context.target))(),
                    Empty(self.context.collection_type)
                )
        else:
            rv = Single(
                self.context.collection_type,
                IRewriter(self.context.target)())

        self.context.symbols.dellevel()
        return rv

class BinaryRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IBinary)

    def __call__(self):
        return Binary(IRewriter(self.context.left)(),
            IRewriter(self.context).get_operator(),
            IRewriter(self.context.right)())

class UnionRewriter(BinaryRewriter):
    implements(IRewriter)
    adapts(IUnion)

    def __call__(self):
        return Union(
            self.context.left.get_collection_type(),
            IRewriter(self.context.left)(),
            IRewriter(self.context.right)())

class DifferRewriter(BinaryRewriter):
    implements(IRewriter)
    adapts(IDiffer)

    def __call__(self):
        return Differ(
            self.context.left.get_collection_type(),
            IRewriter(self.context.left)(),
            IRewriter(self.context.right)())

class AndRewriter(BinaryRewriter):
    implements(IRewriter)
    adapts(IAnd)

    def get_operator(self):
        return Operator('and')

class OrRewriter(BinaryRewriter):
    implements(IRewriter)
    adapts(IOr)

    def get_operator(self):
        return Operator('or')

class PropertyRewriter(BinaryRewriter):
    implements(IRewriter)
    adapts(IProperty)

    def __call__(self):
        return Identifier(
            '.'.join([self.context.left.name, self.context.right.name]))

class AddRewriter(BinaryRewriter):
    implements(IRewriter)
    adapts(IAdd)

    def get_operator(self):
        return Operator('+')

class MulRewriter(BinaryRewriter):
    implements(IRewriter)
    adapts(IMul)

    def get_operator(self):
        return Operator('*')

class SubRewriter(BinaryRewriter):
    implements(IRewriter)
    adapts(ISub)

    def get_operator(self):
        return Operator('-')

class DivRewriter(BinaryRewriter):
    implements(IRewriter)
    adapts(IDiv)

    def get_operator(self):
        return Operator('/')

class NotRewriter(BinaryRewriter):
    implements(IRewriter)
    adapts(INot)

    def __call__(self):
        return Not(IRewriter(self.context.expression)())

class CountRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(ICount)

    def __call__(self):
        return Reduce(
            self.context.expression.collection_type, # FIXME milyen bag
            Constant(0),
            Lambda('i', Constant(1)),
            Operator('+'),
            IRewriter(self.context.expression)()
            # FIXME ?set? must be determined by type(self.expression)
        )

class QuantorRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IQuantor)

    def __call__(self, expression, quanter, operator):
        return NotImplementedError()

class QuentedRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IQuanted)

    def __call__(self, expression, operator):
        return IRewriter(self.context.quantor)(expression, self.context.expression, operator)

class EveryRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(IEvery)

    def __call__(self, expression, quanted, operator):
        ctype = quanted.get_collection_type()

        return Reduce(
            ctype, # FIXME ?set? but which type() to take? quanted.expression?
            Identifier('True'),
            Lambda('i',
                IRewriter(operator.__class__(
                    self.context.metadata,
                    self.context.symbols,
                    ocql.queryobject.queryobject.Identifier(
                        self.context.metadata,
                        self.context.symbols,
                        'i'),
                    expression
                ))()
            ),
            Operator('and'),
            IRewriter(quanted)()
        )

class SomeRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(ISome)

    def __call__(self, expression, quanted, operator):
        ctype = quanted.get_collection_type()
        return Reduce(
            ctype, # FIXME ?set? but which type() to take? quanted.expression?
            Identifier('False'),
            Lambda('i',
                IRewriter(operator.__class__(
                    self.context.metadata,
                    self.context.symbols,
                    ocql.queryobject.queryobject.Identifier(
                        self.context.metadata,
                        self.context.symbols,'i'),
                    expression
                ))()
            ),
            Operator('or'),
            IRewriter(quanted)()
        )

class ConditionRewriter(ChildRewriter):
    implements(IRewriter)
    adapts(ICondition)

    def __call__(self):
        if isinstance(self.context.left, ocql.queryobject.queryobject.Quanted):
            return IRewriter(self.context.left)(self.context.right, self.context)
        if isinstance(self.context.right, ocql.queryobject.queryobject.Quanted):
            return IRewriter(self.context.right)(self.context.left, self.context)
        else:
            return Binary(
                IRewriter(self.context.left)(),
                IRewriter(self.context).get_operator(),
                IRewriter(self.context.right)())

class EqRewriter(ConditionRewriter):
    implements(IRewriter)
    adapts(IEq)

    def get_operator(self):
        return Operator('==')

class NeRewriter(ConditionRewriter):
    implements(IRewriter)
    adapts(INe)

    def get_operator(self):
        return Operator('!=')

class LtRewriter(ConditionRewriter):
    implements(IRewriter)
    adapts(ILt)

    def get_operator(self):
        return Operator('<')

class GtRewriter(ConditionRewriter):
    implements(IRewriter)
    adapts(IGt)

    def get_operator(self):
        return Operator('>')

class LeRewriter(ConditionRewriter):
    implements(IRewriter)
    adapts(ILe)

    def get_operator(self):
        return Operator('<=')

class GeRewriter(ConditionRewriter):
    implements(IRewriter)
    adapts(IGe)

    def get_operator(self):
        return Operator('>=')

#
#def registerAdapters():
#    provideAdapter(IdentifierRewriter)
#    provideAdapter(ConstantRewriter)
#    provideAdapter(QueryRewriter)
#    provideAdapter(BinaryRewriter)
#    provideAdapter(UnionRewriter)
#    provideAdapter(DifferRewriter)
#    provideAdapter(AndRewriter)
#    provideAdapter(OrRewriter)
#    provideAdapter(PropertyRewriter)
#    provideAdapter(AddRewriter)
#    provideAdapter(MulRewriter)
#    provideAdapter(SubRewriter)
#    provideAdapter(DivRewriter)
#    provideAdapter(NotRewriter)
#    provideAdapter(CountRewriter)
#    provideAdapter(QuentedRewriter)
#    provideAdapter(EveryRewriter)
#    provideAdapter(SomeRewriter)
#    provideAdapter(ConditionRewriter)
#    provideAdapter(EqRewriter)
#    provideAdapter(NeRewriter)
#    provideAdapter(LtRewriter)
#    provideAdapter(GtRewriter)
#    provideAdapter(LeRewriter)
#    provideAdapter(GeRewriter)
