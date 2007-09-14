from zope import schema,interface
from interfaces import *

class ViewReferenceField(schema.Object):
    interface.implements(IViewReferenceField)

    def __init__(self,**kw):
        super(ViewReferenceField,self).__init__(IViewReference,
                                                **kw)
        
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

