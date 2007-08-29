from zope import interface
from zope.schema.fieldproperty import FieldProperty
from zope.app.folder.folder import Folder
from zope.app.file.image import Image
from z3c.reference.demo.interfaces import (IDemoFolder,
                                           IDemoImage)
from z3c.reference.interfaces import (IViewReference,
                                     IReferenced)
from z3c.reference.reference import viewReferenceRelated
from lovely.relation.property import (FieldRelationManager,
                                      RelationPropertyOut,
                                      RelationPropertyIn)
from z3c.reference.schema import ViewReferenceProperty

class DemoFolder(Folder):
    interface.implements(IDemoFolder, IReferenced)
    previewImage = ViewReferenceProperty("previewImage")
    assets = ViewReferenceProperty("assets")
    
    viewReferences = RelationPropertyIn(viewReferenceRelated)


class DemoImage(Image):
    interface.implements(IDemoImage, IReferenced)
    viewReferences = RelationPropertyIn(viewReferenceRelated)
