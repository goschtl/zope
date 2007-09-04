from zope import (interface, schema)
from z3c.reference.interfaces import IViewReference
from z3c.reference.schema import ViewReferenceField

class IDemoFolder(interface.Interface):
    """ demo folder"""
    previewImage = ViewReferenceField('previewImage',
                                      viewName=u"",
                                      title=u"previewImage",
                                      required=False)
    #assets = schema.List(title=u"Related",
    #                     value_type=ViewReferenceField(u'demosettings'),
    #                     required=False,
    #                     default=[])
    

class IDemoImage(interface.Interface):
    """ demo image"""

    
# view code example

# field.settings
# component.queryMultiAdapter((context.target, self.request),
# IViewReferenceSettings, name=field.settings)

# definition of settings

#def demoImageSettings(image):


#   return dict(ratio = (16,9))


#def demoFolderPreviewSettings(context):

    
