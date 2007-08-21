from zope import interface,schema
from zope.location.interfaces import ILocation
from zope.app.file.interfaces import IImage
from zope.interface.interfaces import IInterface

class IViewReference(interface.Interface):

    """a reference to a view of an object, by storing the name of the
    view. If the target is None, the view name is supposed to be an
    absolute url to an external target"""

    target = schema.Object(ILocation,required=False,
                           title=u'Target Object')
    view = schema.TextLine(required=False,title=u'View')

class IViewReferenceField(schema.interfaces.IObject):
    """a view reference field"""

class IImageReference(IViewReference):

    """a reference to an image with optional size constraints"""
    target = schema.Object(IImage,required=False,
                           title=u'Target Image')

class IImageReferenceField(schema.interfaces.IObject):
    
    """an image reference field"""

    size = schema.Tuple(title=u'Forced Size',
                        value_type=schema.Int(),
                        required=True,
                        min_length=2,max_length=2)

class IObjectReferenceField(IViewReferenceField):
    
    """a schema based reference field"""

    refSchema = schema.Object(IInterface,
                              title=u'Reference Schema')
