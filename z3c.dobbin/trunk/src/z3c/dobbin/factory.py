from zope import interface
from zope import component

import interfaces
import types

def create(spec):
    # set up mapper
    mapper = interfaces.IMapper(spec)

    # create instance
    return mapper()

@interface.implementer(interfaces.IMapped)
@component.adapter(interface.Interface)
def createInstanceFromItem(item):
    return create(item.__class__)

@interface.implementer(interfaces.IMapped)
@component.adapter(types.IntType)
def createIntegerBasicType(int):
    return create(interfaces.IIntegerBasicType)

@interface.implementer(interfaces.IMapped)
@component.adapter(types.FloatType)
def createFloatBasicType(float):
    return create(interfaces.IFloatBasicType)

@interface.implementer(interfaces.IMapped)
@component.adapter(types.UnicodeType)
def createUnicodeBasicType(str):
    return create(interfaces.IUnicodeBasicType)

@interface.implementer(interfaces.IMapped)
@component.adapter(types.StringType)
def createStringBasicType(str):
    return create(interfaces.IStringBasicType)

@interface.implementer(interfaces.IMapped)
@component.adapter(types.TupleType)
def createTupleBasicType(tuple):
    return create(interfaces.ITupleBasicType)

@interface.implementer(interfaces.IMapped)
@component.adapter(types.ListType)
def createListBasicType(list):
    return create(interfaces.IListBasicType)

@interface.implementer(interfaces.IMapped)
@component.adapter(type(set()))
def createSetBasicType(set):
    return create(interfaces.ISetBasicType)

@interface.implementer(interfaces.IMapped)
@component.adapter(types.DictType)
def createDictBasicType(dict):
    return create(interfaces.IDictBasicType)


