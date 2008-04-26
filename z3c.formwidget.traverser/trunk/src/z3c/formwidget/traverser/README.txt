====================
The Widget Namespace
====================

The widget namespace provides a way to traverse to the widgets of a
formlib form.

  >>> from z3c.formwidget.traverser.namespace import WidgetHandler
  >>> from z3c.form import testing
  >>> testing.setupFormDefaults()  

Let us define a form to test this behaviour.

  >>> from z3c.form import form, field
  >>> from zope import interface, schema
  >>> class IMyContent(interface.Interface):
  ...     title = schema.TextLine(title=u'Title')
  >>> class MyContent(object):
  ...     interface.implements(IMyContent)
  ...     title=None
  >>> content = MyContent()
  >>> request = testing.TestRequest()
  >>> class MyForm(form.EditForm):
  ...     fields = field.Fields(IMyContent)
  >>> view = MyForm(content, request)
  >>> handler = WidgetHandler(view, request)
  >>> handler.traverse('title', None)
  <TextWidget 'form.widgets.title'>
  
