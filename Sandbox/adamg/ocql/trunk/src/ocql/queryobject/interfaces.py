# -*- coding: UTF-8 -*-

from zope.interface import Attribute, Interface
from zope.schema import TextLine

from ocql.interfaces import IObjectQuery

class IObjectQueryChild(Interface):
    """Objects providing this interface represents a child in the query object tree
    """
    children = Attribute('Children collection')

class ITerm(IObjectQueryChild):
    """Objects providing this interface represent the
    Term Query object
    """
    identifier = Attribute('identifier')
    expression = Attribute('attribute')

class IExpression(ITerm, IObjectQuery):
    """Objects providing this interface represent the
    Expression Query object
    """

class IIsinstance(IExpression):
    """Objects providing this interface represent the
    isinstance Query object
    """
    objekt = Attribute('object')
    tipe = Attribute('type')

class IhasClassWith(IExpression):
    """Objects providing this interface represent the
    hasClassWith Query object
    """
    expression = Attribute('expression')
    klass = Attribute('collection type')
    conditional = Attribute('conditional')

class IIdentifier(IExpression):
    """Objects providing this interface represent the
    Identifier Query object
    """
    name = TextLine()

class IConstant(IExpression):
    """Objects providing this interface represent the
    Constant Query object
    """
    value = Attribute('constant value')

class IStringConstant(IConstant):
    """Objects providing this interface represent the
    StringConstant Query object
    """

class INumericConstant(IConstant):
    """Objects providing this interface represent the
    NumericConstant Query object
    """

class IBooleanConstant(IConstant):
    """Objects providing this interface represent the
    BooleanConstant Query object
    """

class ICollectionConstant(IConstant):
    """Objects providing this interface represent the
    CollectionConstant Query object
    """

class IQuery(IExpression):
    """Objects providing this interface represent the
    Query object
    """
    collection_type = Attribute('collection type')
    terms = Attribute('terms')
    target = Attribute('target')

class IIn(ITerm):
    """Objects providing this interface represent the
    In Query object
    """

class IAlias(ITerm):
    """Objects providing this interface represent the
    Alias Query object
    """

class IBinary(IExpression):
    """Objects providing this interface represent the
    Binary Query object
    """
    left = Attribute('left side of the binary expression')
    right = Attribute('right side of the binary expression')

class IUnion(IBinary):
    """Objects providing this interface represent the
    Union Query object
    """

class IDiffer(IBinary):
    """Objects providing this interface represent the
    Differ Query object
    """

class IAnd(IBinary):
    """Objects providing this interface represent the
    And Query object
    """

class IOr(IBinary):
    """Objects providing this interface represent the
    Or Query object
    """

class IProperty(IBinary):
    """Objects providing this interface represent the
    Property Query object
    """

class IIndex(IBinary):
    """Objects providing this interface represent the
    Index Query object
    """

class IArithmetic(IBinary):
    """Objects providing this interface represent the
    Arithmetic Query object
    """

class IAdd(IArithmetic):
    """Objects providing this interface represent the
    Add Query object
    """
class IMul(IArithmetic):
    """Objects providing this interface represent the
    Multiplication Query object
    """

class ISub(IArithmetic):
    """Objects providing this interface represent the
    Subtract Query object
    """

class IDiv(IArithmetic):
    """Objects providing this interface represent the
    Division Query object
    """

class IUnary(IExpression):
    """Objects providing this interface represent the
    Unary Query object
    """
    expression = Attribute('expression')

class INot(IUnary):
    """Objects providing this interface represent the
    Not Query object
    """

class IAggregate(IUnary):
    """Objects providing this interface represent the
    Aggregate Query object
    """

class ICount(IAggregate):
    """Objects providing this interface represent the
    Count Query object
    """

class ISum(IAggregate):
    """Objects providing this interface represent the
    Sum Query object
    """

class IQuantor(IObjectQuery):
    """Objects providing this interface represent the
    Quantor Query object
    """
    expr = Attribute('expression')

class IQuanted(IObjectQueryChild):
    """Objects providing this interface represent the
    Quanted Query object
    """
    quantor = Attribute('quantor')
    expression = Attribute('expression')

class IEvery(IQuantor):
    """Objects providing this interface represent the
    Every Query object
    """

class ISome(IQuantor):
    """Objects providing this interface represent the
    Some Query object
    """

class IAtmost(IQuantor):
    """Objects providing this interface represent the
    Atmost Query object
    """

class IAtleast(IQuantor):
    """Objects providing this interface represent the
    Atleast Query object
    """

class IJust(IQuantor):
    """Objects providing this interface represent the
    Just Query object
    """

class ICondition(IExpression):
    """Objects providing this interface represent the
    Condition Query object
    """
    left = Attribute('left side of the condition')
    right = Attribute('right side of the condition')

class IEq(ICondition):
    """Objects providing this interface represent the
    Equal Query object
    """

class INe(ICondition):
    """Objects providing this interface represent the
    Negation Query object
    """

class ILt(ICondition):
    """Objects providing this interface represent the
    Less than Query object
    """

class IGt(ICondition):
    """Objects providing this interface represent the
    Greater than Query object
    """

class ILe(ICondition):
    """Objects providing this interface represent the
    Less than or Equal Query object
    """

class IGe(ICondition):
    """Objects providing this interface represent the
    Greater than or Equal Query object
    """
