# -*- coding: UTF-8 -*-

from ocql.interfaces import IAlgebraObject
from zope.schema import Dict, Text
from zope.interface import Attribute

################
#Algebra operation interfaces
################

class IEmpty(IAlgebraObject):
    """Objects providing this interface represent the
    Empty Algebra object
    """ 
    klass = Attribute('collection type name')
    expr = Attribute('expression')


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

    
class IIter(IAlgebraObject):
    """Objects providing this interface represent the
    Iter Algebra object
    """
    klass = Attribute('collection type name')
    fun = Attribute('function')
    coll = Attribute('collection')
    

class ISelect(IAlgebraObject):
    """Objects providing this interface represent the
    Select Algebra object
    """
    klass = Attribute('collection type name')
    fun = Attribute('function')
    coll = Attribute('collection')
    

class IReduce(IAlgebraObject):
    """Objects providing this interface represent the
    Reduce Algebra object
    """
    klass = Attribute('collection type name')
    expr = Attribute('expression')
    fun = Attribute('function')
    aggreg = Attribute('aggregation')
    coll = Attribute('collection')
    

class IOperator(IAlgebraObject):
    """Objects providing this interface represent the
    Operator Algebra object
    """
    ops = Dict(Text(), Text())
    op = Text()
    
    
class IRange(IAlgebraObject):
    """Objects providing this interface represent the
    Range Algebra object
    """
    
class IMake(IAlgebraObject):
    """Objects providing this interface represent the
    Make Algebra object
    """
    
class IIf(IAlgebraObject):
    """Objects providing this interface represent the
    If Algebra object
    """
    
class ILambda(IAlgebraObject):
    """Objects providing this interface represent the
    Lambda Algebra object
    """
    
class IConstant(IAlgebraObject):
    """Objects providing this interface represent the
    Constant Algebra object
    """
    
class IIdentifier(IAlgebraObject):
    """Objects providing this interface represent the
    Identifier Algebra object
    """
    
class IBinery(IAlgebraObject):
    """Objects providing this interface represent the
    Binery Algebra object
    """
    
