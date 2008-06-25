from zope import interface
from zope import schema

class IMapped(interface.Interface):    
    __mapper__ = interface.Attribute(
        """ORM mapper.""")

class IMapper(interface.Interface):
    """An ORM mapper for a particular specification."""

class IBasicType(interface.Interface):
    """A basic Python value type."""

class IIntegerBasicType(IBasicType):
    value = schema.Int()

class IFloatBasicType(IBasicType):
    value = schema.Float()
    
class IUnicodeBasicType(IBasicType):
    value = schema.Text()
    
class IStringBasicType(IBasicType):
    value = schema.Bytes()

class ITupleBasicType(IBasicType):
    value = schema.Tuple()

class IListBasicType(IBasicType):
    value = schema.List()

class ISetBasicType(IBasicType):
    value = schema.Set()

class IDictBasicType(IBasicType):
    value = schema.Dict()
    
