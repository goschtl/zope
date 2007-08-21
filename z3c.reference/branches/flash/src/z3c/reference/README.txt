=========================
 Refererences to Objects
=========================

Referenced objects must be adaptable to IKeyReference.

  >>> from z3c.reference.reference import ViewReference
  >>> from zope.annotation.interfaces import IAttributeAnnotatable
  >>> from zope.app.container.contained import Contained
  >>> from zope import interface
  >>> class O(Contained):
  ...     interface.implements(IAttributeAnnotatable)
  ...     def __init__(self,title):
  ...         if title is not None:
  ...             self.title = title

  >>> o = O(u"first")
  >>> o.title
  u'first'

  >>> ref = ViewReference(target=o)
  >>> ref.target is o
  True

  If we do not define a target the view is supposed to be absolute
  url. No further checks are done.

  >>> ref = ViewReference(view=u'abc')
  >>> ref.target is None
  True



Reference Fields
================

  >>> from zope.schema.fieldproperty import FieldProperty
  >>> from z3c.reference.schema import ViewReferenceField
  >>> 
  >>> class IContent(interface.Interface):
  ...     ref = ViewReferenceField(title=u"Reference")
  >>> class Content(object):
  ...     interface.implements(IContent)
  ...     ref = FieldProperty(IContent['ref'])

  >>> c = Content()
  >>> c.ref is None
  True
  >>> c.ref = object()
  Traceback (most recent call last):
  ...
  SchemaNotProvided
  >>> o2 = O(u'O2 Title')
  >>> c.ref = ViewReference(o2)
  >>> c.ref.target is o2
  True
  
Image Reference Fields
======================

ImageReferenceField is a special ViewReferenceField, which constraints
the size and the object type to IImage

  >>> from z3c.reference.reference import ImageReference
  >>> from z3c.reference.schema import ImageReferenceField
  >>> from zope.schema.fieldproperty import FieldProperty

  On  Image references the size is required.

  >>> class IContent(interface.Interface):
  ...     img = ImageReferenceField(title=u"Image",size=(10,10))
  >>> class Content(object):
  ...     interface.implements(IContent)
  ...     img = FieldProperty(IContent['img'])

  >>> c = Content()
  >>> c.img is None
  True
  >>> c.img = object()
  Traceback (most recent call last):
  ...
  SchemaNotProvided
  >>> from zope.app.file.image import Image
  >>> from zope.app.file.interfaces import IImage
  >>> img = Image()
  >>> imgRef = ImageReference(img)
  >>> imgRef
  <z3c.reference.reference.ImageReference object at ...>

  >>> IContent['img'].schema.providedBy(imgRef)
  True

  >>> c.img = imgRef
  >>> c.img.target is img
  True


