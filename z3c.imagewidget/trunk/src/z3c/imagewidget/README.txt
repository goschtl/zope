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
  '.../++session++z3c.sessionwidget.SessionInputWidget/field./++item++data/'

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


TO DO
-----

Use PIL to enforce size.
