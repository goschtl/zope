========================
The Session Input Widget
========================

Sometimes fields do not describe just simple data types, but complex data
structures. In those scenarios, widgets of the field do not represent a simple
text input or a small set of input elements, but more complex
combinations. Until now, those scenarios were solved using either sub-forms or
a fairly complicated widget for the object field.

While a sub-form is an acceptable solution, it often writes the data to the
object before the form's save button is pressed. This is, for example, the
case when uploading images and displaying them right away as visual
feedback. The object widget has the same problem when constructing sequences
with complex sub-items. In general it is up to the developer to decide when to
present a new form or use the widget, but at least s/he should have the
choice.

To solve this problem, this package provides a widget that is only responsible
for relaying the data of interest to a session. A sub-form or any other
component can then use this session data and provide new data, if desired. The
session data will also be publically available via a URL, so that the objects
can also be displayed, such as images. This has the advantage that the data is
*not* stored on the content until the overall form is submitted.

The session has two data fields:

1. data --> The data object of interest as it will be stored in the content
            object.

2. changed --> A boolean saying whether the data has changed.

Usually, sub-forms work with those two data fields and update the new data. To
demonstrate this we first need to create a schema for the object and the
content containing the object,

  >>> import zope.interface
  >>> import zope.schema

The widget class implements IInputWidget, this is needed in order to
be handled as such in forms.

  >>> from z3c.sessionwidget import widget
  >>> from zope.app.form.interfaces import IInputWidget
  >>> from zope.interface import verify
  >>> verify.verifyClass(IInputWidget, widget.SessionInputWidget)
  True

  >>> class IObject(zope.interface.Interface):
  ...     '''An object in the content.'''

  >>> class IContent(zope.interface.Interface):
  ...     obj = zope.schema.Object(
  ...         title=u'Object',
  ...         schema=IObject)

implement those interfaces,

  >>> class Object(object):
  ...     zope.interface.implements(IObject)
  ...     def __init__(self, id):
  ...         self.id = id
  ...     def __repr__(self):
  ...         return '<%s %s>' %(self.__class__.__name__, self.id)

  >>> class Content(object):
  ...     zope.interface.implements(IContent)
  ...     obj = zope.schema.fieldproperty.FieldProperty(IContent['obj'])

and finally instantiate the content:

  >>> content = Content()

After creating a request,

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

we can now initialize the widget:

  >>> objWidget = widget.SessionInputWidget(IContent['obj'], request)
  >>> verify.verifyObject(IInputWidget, objWidget)
  True

The widget can directly access the session:

  >>> objWidget.session
  <zope.session.session.SessionPkgData object at ...>
  >>> objWidget.session.get('data', 'nothing')
  'nothing'
  >>> objWidget.session.get('changed', 'nothing')
  'nothing'

Initially, the widget has no data:

  >>> objWidget.hasInput()
  False

Input widgets require that input be available in the form request. If
input is not present, a ``MissingInputError`` is raised:

  >>> objWidget.getInputValue()
  Traceback (most recent call last):
  ...
  MissingInputError: ('field.obj', u'Object', None)

This is satisfied by using a hidden field.

  >>> request.form['field.obj.used'] = ''
  >>> objWidget.hasInput()
  True
  >>> objWidget.getInputValue() is None
  Traceback (most recent call last):
  ...
  WidgetInputError: ('obj', u'Object', RequiredMissing('obj'))

Ups, we have a required field, so we need an accecptable Value. We can
achieve this by setting the rendered value.

  >>> objWidget.setRenderedValue(Object('1'))
  >>> objWidget.getInputValue()
  <Object 1>

Let's now say that some arbitrary form creates a new object.

  >>> objWidget.session['data'] = Object('2')

This form is also responsible for setting the changed flag:

  >>> objWidget.session['changed'] = True

Now the input value is different:

  >>> objWidget.getInputValue()
  <Object 2>

Also, setting the rendered value is now ineffective:

  >>> objWidget.setRenderedValue(Object('1'))
  >>> objWidget.getInputValue()
  <Object 2>

When applying the changes, the method only looks at the changed flag to decide
whether the data changed:

  >>> content.obj is None
  True
  >>> objWidget.applyChanges(content)
  True
  >>> content.obj
  <Object 2>

Note that calling thos method also resets the session:

  >>> objWidget.session['data']
  >>> objWidget.session['changed']

Note that hidden always renders the marker field, so that the parent
form knows that the widget was rendered.

  >>> print objWidget.hidden()
  <input ... name="field.obj.used" type="hidden" value="" />

Let's now set a new object value again, but changing the changed flag. No
changes will be applied:

  >>> objWidget.session['data'] = Object('3')
  >>> objWidget.session['changed'] = False

  >>> content.obj
  <Object 2>
  >>> objWidget.applyChanges(content)
  False
  >>> content.obj
  <Object 2>


TO DO:
------

The id identifying the session data is not unique enough; we need some better
mechanism for this later.
