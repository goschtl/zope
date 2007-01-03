================
The Image Widget
================

This package really does not provide any widget code at all, but is a set of
forms that work with the session widget to provide an image upload and display
*before* the data is stored in the content. Thus the following tests will
simply test the various forms.

  >>> from z3c.imagewidget import form, widget

Adding an Image
---------------

The add form is a view on the image (session) widget and the request:

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

  >>> import zope.schema
  >>> from zope.app.file.interfaces import IImage
  >>> imgField = zope.schema.Object(
  ...     __name__=u'img',
  ...     title=u'Image', schema=IImage)

  >>> imgWidget = widget.ImageInputWidget(imgField, request)
  >>> imgWidget.session.get('data')
  >>> imgWidget.session.get('changed')

  >>> addForm = form.AddImageForm(imgWidget, request)
  >>> addForm.createAndAdd({'data': '%PNG...'})

  >>> imgWidget.session['data']
  <zope.app.file.image.Image object at ...>
  >>> imgWidget.session['changed']
  True

Let's also make sure that the image data is what it needs to be:

  >>> imgWidget.session['data'].data
  '%PNG...'


Editing an Image
----------------

Now that we have an image we can change it.

  >>> image = imgWidget.session['data']
  >>> imgWidget.session['changed'] = False

  >>> editForm = form.EditImageForm(image, request)
  >>> editForm.widget = imgWidget
  >>> editForm.adapters = {}
  >>> editForm.handle_edit_action.success({'data': '%PNG2...'})

  >>> editForm.status
  u'Image updated.'
  >>> imgWidget.session['data'].data
  '%PNG2...'
  >>> imgWidget.session['changed']
  True

You can also generate the URL for the image for display:

  >>> editForm.imageURL
  u'.../++session++z3c.sessionwidget.SessionInputWidget/field.img/++item++data?ts=0'

When uploading an empty image, the image is set to None:

  >>> imgWidget.session['changed'] = False

  >>> editForm.handle_edit_action.success({'data': ''})

  >>> imgWidget.session['data']
  >>> imgWidget.session['changed']
  True


The Controller Form
-------------------

The controller form manages the forms to be displayed. So let's restart the
example above and make sure everything works:

  >>> imgWidget.name = 'data'

  >>> imgWidget.session['data'] = None
  >>> imgWidget.session['changed'] = False

We also need some component setup:

  >>> import zope.component
  >>> from zope.app.form.browser import BytesWidget
  >>> from zope.schema.interfaces import IBytes
  >>> from zope.app.form.interfaces import IInputWidget

  >>> zope.component.provideAdapter(
  ...    BytesWidget, (IBytes, TestRequest), IInputWidget)

At the beginning we have an add form, since no image is available as input:

  >>> widgetForm = form.ImageSessionWidgetForm(imgWidget, request)
  >>> widgetForm.update()
  >>> widgetForm.imageForm
  <z3c.imagewidget.form.AddImageForm object at ...>

If we now upload an image, we end at an edit form:

  >>> request = TestRequest(form={
  ...     'imageForm.data': '%PNG...',
  ...     'imageForm.actions.add': ''})

  >>> widgetForm = form.ImageSessionWidgetForm(imgWidget, request)
  >>> widgetForm.update()
  >>> widgetForm.imageForm
  <z3c.imagewidget.form.EditImageForm object at ...>

  >>> imgWidget.session['data'].data
  '%PNG...'

Now let's change the image and we get back the edit form:

  >>> request = TestRequest(form={
  ...     'imageForm.data': '%PNG2...',
  ...     'imageForm.actions.55706461746520696d616765': ''})

  >>> widgetForm = form.ImageSessionWidgetForm(imgWidget, request)
  >>> widgetForm.update()
  >>> widgetForm.imageForm
  <z3c.imagewidget.form.EditImageForm object at ...>

  >>> imgWidget.session['data'].data
  '%PNG2...'

Passing empty data should give us back the add form.

  >>> request = TestRequest(form={
  ...     'imageForm.data': '',
  ...     'imageForm.actions.55706461746520696d616765': ''})

  >>> widgetForm = form.ImageSessionWidgetForm(imgWidget, request)
  >>> widgetForm.update()
  >>> widgetForm.imageForm
  <z3c.imagewidget.form.AddImageForm object at ...>


Enforcing Display Size of an Image
----------------------------------

To enforce the size of an image, we have to subclass the ImageWidget
and provide class attributes on the widget.

  >>> class MySizedImageWidget(widget.ImageInputWidget):
  ...     width = 100
  ...     height = 100

In order to test this we need a real image, which we get from the
testing package of z3c.image.

  >>> from z3c.image import testing
  >>> image = testing.getTestImage('flower.jpg')
  >>> image.getImageSize()
  (103, 118)

We have defined the size constraint to 100, 100 so the image should be
resized if we add the value.

  >>> imgWidget = MySizedImageWidget(imgField, request)
  >>> imgWidget.name='data'
  >>> imgWidget.session['changed']=False
  >>> imgWidget.session['data']=None
  >>> addForm = form.AddImageForm(imgWidget, request)
  >>> addForm.createAndAdd({'data': image.data})
  >>> imgWidget.session['data'].getImageSize()
  (87, 100)

Also the edit form resizes the image if needed.

  >>> editForm = form.EditImageForm(imgWidget.session['data'], request)
  >>> editForm.widget = imgWidget
  >>> editForm.adapters = {}
  >>> editForm.handle_edit_action.success({'data': image.data})

So now we have no changes, since we resized the same image as
before.

  >>> imgWidget.session['data'].getImageSize()
  (87, 100)
  >>> editForm.status
  ''

So let us define some other data.

  >>> editForm.handle_edit_action.success({'data': '%PNG...'})
  >>> editForm.status
  u'Image updated.'

This was no real image data, so no size information can be
extracted. The resizing does not happen.

  >>> imgWidget.session['data'].getImageSize()
  (-1, -1)

We now send our flower image again. Which is still larger than 100, 100
of course.

  >>> image.getImageSize()
  (103, 118)
  >>> editForm.status = ''
  >>> editForm.handle_edit_action.success({'data': image.data})
  >>> editForm.status
  u'Image updated.'

And is now resized.

  >>> imgWidget.session['data'].getImageSize()
  (87, 100)

