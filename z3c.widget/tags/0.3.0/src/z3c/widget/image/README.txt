================
The Image Widget
================

this image widget should be used as a custom_widget for image fields.
comparing to the default widget in zope3 it does not delete the
data in the field if the "delete" checkbox is not explicitly selected.


Adding an Image
===============

  >>> import zope.schema
  >>> from zope.publisher.browser import TestRequest
  >>> from zope import interface
  >>> from zope.schema.fieldproperty import FieldProperty
  >>> from zope.app.file.interfaces import IImage
  >>> from z3c.widget.image.widget import ImageWidget
  >>> from zope.app.file.image import Image


create a content type with an image field.

  >>> class ITestObject(interface.Interface):
  ...     image = zope.schema.Object(
  ...     title=u'Image',
  ...     schema=IImage)
  >>> class TestObject(object):
  ...     interface.implements(ITestObject)
  ...     image = FieldProperty(ITestObject['image'])

  >>> obj = TestObject()

  >>> field = ITestObject['image'].bind(obj)


Send the request without any image information. the empty field
should not be changed...

  >>> request = TestRequest(form={'field.image' : u''})
  >>> widget = ImageWidget(field, request)
  >>> widget._getFormInput() is None
  True

Send some Image information to the field. the image information
should be stored in the field as a Image Object

  >>> request = TestRequest(form={'field.image' : u'PNG123Test'})
  >>> widget = ImageWidget(field, request)
  >>> widget._getFormInput()
  <zope.app.file.image.Image object at ...>


Now we save the field again, but without any new image data.
the old image information should not be lost

  >>> obj.image = Image(u'PNG123Test')
  >>> request = TestRequest(form={'field.image' : u''})
  >>> widget = ImageWidget(field, request)
  >>> widget._getFormInput() is obj.image
  True

Now we want to delete the image. the forminput should be None now.

  >>> request = TestRequest(form={'field.image' : u'',
  ...     'field.image.delete': u'true'})
  >>> widget = ImageWidget(field, request)
  >>> widget._getFormInput() is None
  True

  >>> print widget()
  <div class="z3cImageWidget">
    <input type="file" name="field.image" id="field.image" /><br/>
    <input type="checkbox" name="field.image.delete" value="true" />delete image
  </div>




