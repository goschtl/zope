# -*- coding: UTF-8 -*-

from ocql.interfaces import IAlgebraObject
from zope.schema import Dict, Text, Int, TextLine
from zope.interface import Attribute, Interface

################
#Algebra operation interfaces
################

class IEmpty(IAlgebraObject):
    """Objects providing this interface represent the
    Empty Algebra object
    """
    klass = Attribute('collection type name')

class ISingle(IAlgebraObject):
    """Objects providing this interface represent the
    Single Algebra object
    """
    klass = Attribute('collection type name')
    expr = Attribute('expression')

class IUnion(IAlgebraObject):
    """Objects providing this interface represent the
    Union Algebra object
    """
    klass = Attribute('collection type name')
    coll1 = Attribute('first collection')
    coll2 = Attribute('second collection')

class IDiffer(IAlgebraObject):
    """Objects providing this interface represent the
    Union Algebra object
    """
    klass = Attribute('collection type name')
    coll1 = Attribute('first collection')
    coll2 = Attribute('second collection')

class INot(IAlgebraObject):
    """Objects providing this interface represent the
    Not Algebra object
    """
    klass = Attribute('collection type name')
    coll = Attribute('collection')

class IIter(IAlgebraObject):
    """Objects providing this interface represent the
    Iter Algebra object
    """
    klass = Attribute('collection type name')
    func = Attribute('function')
    coll = Attribute('collection')

class ISelect(IAlgebraObject):
    """Objects providing this interface represent the
    Select Algebra object
    """
    klass = Attribute('collection type name')
    func = Attribute('function')
    coll = Attribute('collection')

class IReduce(IAlgebraObject):
    """Objects providing this interface represent the
    Reduce Algebra object
    """
    klass = Attribute('collection type name')
    expr = Attribute('expression')
    func = Attribute('function')
    aggreg = Attribute('aggregation')
    coll = Attribute('collection')

class IRange(IAlgebraObject):
    """Objects providing this interface represent the
    Range Algebra object
    """
    klass = Attribute('collection type name')
    start = Attribute('range start point')
    end = Attribute('range end point')

class IMake(IAlgebraObject):
    """Objects providing this interface represent the
    Make Algebra object
    """
    expr = Attribute('expression')
    coll1 = Attribute('first collection')
    coll2 = Attribute('second collection')

class IMakeFromIndex(IAlgebraObject):
    """Objects providing this interface represent the
    MakeFromIndex Algebra object
    """
    expr1 = Attribute('expression1')
    expr2 = Attribute('expression2')
    coll1 = Attribute('first collection')
    coll2 = Attribute('second collection')
    operator = Attribute('operator')
    value = Attribute('boundary value of the query')

class IIf(IAlgebraObject):
    """Objects providing this interface represent the
    If Algebra object
    """
    cond = Attribute('condition')
    expr1 = Attribute('first expression')
    expr2 =Attribute('second expression')

class ILambda(IAlgebraObject):
    """Objects providing this interface represent the
    Lambda Algebra object
    """
    var = Attribute('variable')
    expr = Attribute('expression')

class IConstant(IAlgebraObject):
    """Objects providing this interface represent the
    Constant Algebra object
    """
    value = Attribute('constant value')

class IIdentifier(IAlgebraObject):
    """Objects providing this interface represent the
    Identifier Algebra object
    """
    name = Text()

class IBinary(IAlgebraObject):
    """Objects providing this interface represent the
    Binery Algebra object
    """
    left = Attribute('left expression')
    op = Attribute('operator')
    right = Attribute('right expression')

class IOperator(IAlgebraObject):
    """Objects providing this interface represent the
    Operator Algebra object
    """
#    ops = Dict(Text(), Text())
    op = Text()
