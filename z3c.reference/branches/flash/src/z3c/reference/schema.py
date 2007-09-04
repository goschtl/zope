from zope import schema,interface
from interfaces import *
import types

class ViewReferenceField(schema.Object):
    interface.implements(IViewReferenceField)

    def __init__(self, viewName=None, **kw):
        self.viewName = viewName
        super(ViewReferenceField,self).__init__(IViewReference,
                                                **kw)

        
class ViewReferenceProperty(property):
    """A property that takes care of setting __parent__ for all reference
    objects when being set on the content object.
    """
    
    def __init__(self, name):
        self.name = "_%s" % name

    def __get__(self, obj, default=None):
        return getattr(obj, self.name, default)

    def __set__(self, obj, value):
        if type(value) in (types.ListType, types.TupleType):
            for ref in value:
                ref.__parent__ = obj
        else:
            value.__parent__ = obj
        setattr(obj, self.name, value)

    
class ImageReferenceField(schema.Object):
    interface.implements(IImageReferenceField)
    size = schema.fieldproperty.FieldProperty(IImageReferenceField['size'])
    
    def __init__(self,**kw):
        self.size = kw.pop('size',None)
        super(ImageReferenceField,self).__init__(IImageReference,
                                                 **kw)


class ObjectReferenceField(ViewReferenceField):
    interface.implements(IObjectReferenceField)

    def __init__(self,refSchema,**kw):
        self.refSchema = refSchema
        super(ObjectReferenceField,self).__init__(**kw)

