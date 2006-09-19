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
qith complex sub-items. In general it is up to the developer to decide when to
present a new form or use the widget, but at least s/he should have the
choice.

To solve this problem, this package provides a widget that is only responsible
for relaying the data of interest to a session. A sub-form or any other
componentcan then use this session data and provide new data, if desired. The
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

  >>> from z3c.sessionwidget import widget
  >>> objWidget = widget.SessionInputWidget(IContent['obj'], request)

The widget can directly access the session:

  >>> objWidget.session
  <zope.app.session.session.SessionPkgData object at ...>
  >>> objWidget.session.get('data', 'nothing')
  'nothing'
  >>> objWidget.session.get('changed', 'nothing')
  'nothing'

Initially, the widget has no data:

  >>> objWidget.hasInput()
  False

Once we set the rendered value, we have soem input:

  >>> objWidget.setRenderedValue(Object('1'))
  >>> objWidget.hasInput()
  True

Of course, you can now retrieve that value:

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

  >>> content.obj

  >>> objWidget.applyChanges(content)
  True

  >>> content.obj
  <Object 2>

Note that calling thos method also resets the session:

  >>> objWidget.session['data']
  >>> objWidget.session['changed']

Note that hidden always renders empty:

  >>> objWidget.hidden()
  ''

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
