======
README
======

The jquery.resteditorre package provides a javascript which can render a 
toolbar above a testarea widget. This toolbar offers buttons which can be used 
for apply reStructuredText formatters to the text in the textarea. 

We can't demonstrate this here because it's all done in javascript. The 
reStructuredText editor textarea looks exactly how a normal z3c.form textarea 
looks. Btw. any textarea can use this package, there is no need for using the 
implemented RESTEditorWidget. But anyway such a textarea widget looks like:

  >>> import zope.schema
  >>> from z3c.form import widget
  >>> from z3c.form import testing
  >>> from jquery.widget.resteditor.browser import RESTEditorFieldWidget

We have to define a text field and a test request for instantiate the widget:

  >>> text = zope.schema.Text(
  ...     title=u'Text',
  ...     description=u'Text field'
  ...     )
  >>> widget = RESTEditorFieldWidget(text, testing.TestRequest())
  >>> widget
  <RESTEditorWidget ''>

Before we can render the widget, we need to register a template This template
is normaly registered by the z3c.form framework. Let's do it here since we not
use a real site setup.

  >>> from zope.configuration import xmlconfig
  >>> import zope.component
  >>> import z3c.form
  >>> xmlconfig.XMLConfig('meta.zcml', zope.component)()
  >>> xmlconfig.XMLConfig('meta.zcml', z3c.form)()
  >>> xmlconfig.XMLConfig('configure.zcml', z3c.form)()

Now we can render the widget:

  >>> widget.update()
  >>> print widget.render()
  <textarea id="" name="" class="restEditorWidget"></textarea>

As you can see the reStructuredText editor widget uses a css class called 
``restEditorWidget``. this class can be used for apply a JQuery xpath rule
and load the JQuery method restEditor.

This can be done like:

  $('.restEditorWidget').restEditor();

Of corse you can do this inside a global JQuery dom onload event handler call.
If so, you can use something like this:

  $(document).ready(function() {
      $('.restEditorWidget').restEditor();
  });

Note, there is also a sample located at http://www.z3c.org/samples
