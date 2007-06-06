==========
z3c.formjs
==========

The z3c.formjs package provides additional support for javascript and
ajax for the z3c.form package.

  >>> from z3c.formjs import interfaces as jsinterfaces

Events
======

z3c.formjs.jsevent provides tools for working with javascript events.

  >>> from z3c.formjs import jsevent

There are all the javascript event types reproduced in python:

  >>> jsevent.CLICK
  <JSEvent "click">
  >>> jsevent.DBLCLICK
  <JSEvent "dblclick">
  >>> jsevent.CHANGED
  <JSEvent "changed">
  >>> jsevent.LOAD
  <JSEvent "load">

These are actually objects that implement IJSEvent.

  >>> jsinterfaces.IJSEvent.providedBy(jsevent.CLICK)
  True

TODO: Find out what all the other javascript events are and stick them
in here.

These events have javascript handlers which can be dynamically
generated so we will define a handler using a function.

  >>> def simpleHandler():
  ...     return 'alert("Some event was called!");'

Another aspect of javascript events is that they get attached to a
specific dom element using an id.  So let us make an imaginary dom
element id.

  >>> id = "form-field-age"

Different javascript libraries handle events in different ways, so we
have to specify which javascript library we want to use to handle the
events so as to render the javascript correctly.  This is done using
browser layers.  The formjs framework implements renderers for
jquery.  The rendered are registered as adapters as follows.

  >>> import zope.component
  >>> zope.component.provideAdapter(jsevent.JQueryEventRenderer)

  >>> from z3c.formjs.testing import TestRequest
  >>> from jquery.layer import IJQueryJavaScriptBrowserLayer
  >>> request = TestRequest()
  >>> IJQueryJavaScriptBrowserLayer.providedBy(request)
  True

  >>> renderer = zope.component.getMultiAdapter((jsevent.CLICK,
  ...                                            request), jsinterfaces.IJSEventRenderer)
  >>> renderer.render(simpleHandler, id)
  '$("#form-field-age").bind("click", function(){alert("Some event was called!");});'


Buttons
=======

z3c.form defines buttons that always submit forms.  It is also highly
useful to have buttons in your form that modify that perform a client
side action using javascript.  z3c.formjs.button provides buttons with
javascript event hooks.

  >>> from z3c.formjs import jsbutton

JSButton
--------

Just as in z3c.form, we can define buttons in a schema.

  >>> import zope.interface
  >>> class IButtons(zope.interface.Interface):
  ...     apply = jsbutton.JSButton(title=u'Apply')
  ...     cancel = jsbutton.JSButton(title=u'Cancel')

From the button creation aspect, everything works exactly as in
z3c.form.  The difference comes with the actions.  We will create a
form that provides these buttons with javascript actions.

  >>> from z3c.form import button
  >>> from z3c.form import interfaces
  >>> class Form(object):
  ...     zope.interface.implements(
  ...         interfaces.IButtonForm, interfaces.IHandlerForm)
  ...     buttons = button.Buttons(IButtons)
  ...     prefix = 'form'
  ...
  ...     @jsbutton.handler(IButtons['apply'])
  ...     def apply(self, action):
  ...         return 'alert("You Clicked the Apply Button!");'
  ...
  ...     @jsbutton.handler(IButtons['cancel'], event=jsevent.DBLCLICK)
  ...     def cancel(self, action):
  ...         return 'alert("You Double Clicked the Cancel Button!");'

Notice that the jsbutton.handler decorator takes the keyword argument
event, which specifies what type of javascript event this handler will
be attached to.

Now we can create the button action manager just as we do with regular
buttons

Let' now create an action manager for the button manager in the form. To do
that we first need a request and a form instance:

  >>> request = TestRequest()
  >>> form = Form()

Action managers are instantiated using the form, request, and
context/content. A special button-action-manager implementation is avaialble
in the ``jsbutton`` package:

  >>> actions = jsbutton.JSButtonActions(form, request, None)
  >>> actions.update()

Once the action manager is updated, the buttons should be available as
actions:

  >>> actions.keys()
  ['apply', 'cancel']
  >>> actions['apply']
  <JSButtonAction 'form.buttons.apply' u'Apply'>

JSButton actions are locations:

  >>> apply = actions['apply']
  >>> apply.__name__
  'apply'
  >>> apply.__parent__
  <JSButtonActions None>

A button action is also a button widget. The attributes translate as follows:

  >>> jsinterfaces.IButtonWidget.providedBy(apply)
  True

Next we want to display our button actions. To be able to do this, we have to
register a template for the button widget:

  >>> from z3c.formjs import testing as jstesting
  >>> from z3c.form import widget
  >>> templatePath = jstesting.getPath('button_input.pt')
  >>> factory = widget.WidgetTemplateFactory(templatePath, 'text/html')

  >>> from zope.pagetemplate.interfaces import IPageTemplate
  >>> zope.component.provideAdapter(factory,
  ...     (zope.interface.Interface, TestRequest, None, None,
  ...      jsinterfaces.IButtonWidget),
  ...     IPageTemplate, name='input')

A widget template has many discriminators: context, request, view, field, and
widget. We can now render each action:

  >>> print actions['apply'].render()
  <input type="button" id="form.buttons.apply"
         name="form.buttons.apply" class="buttonWidget"
         value="Apply"
         onClick="alert("You Clicked the Apply Button!");"/>

  >>> print actions['cancel'].render()
  <input type="button" id="form.buttons.apply"
         name="form.buttons.apply" class="buttonWidget"
         value="Apply"
         onDblClick="alert("You Double Clicked the Cancel Button!");"/>

  
=======
Widgets
=======

Buttons are not the only dom elements that can have events attached to
them, in reality we should be able to attach events to any element of
the form; that is, to any widget in the form.

Creating a Widget and Attaching an Event
----------------------------------------

Taking from the widget.txt file in z3c.form, we will set up a widget
with its own widget template, et cetera, to work with.

  >>> from z3c.form.testing import TestRequest
  >>> from z3c.form import widget
  >>> request = TestRequest()
  >>> age = widget.Widget(request)

  >>> age.name = 'age'
  >>> age.label = u'Age'
  >>> age.value = '39'

  >>> import tempfile
  >>> textWidgetTemplate = tempfile.mktemp('text.pt')
  >>> open(textWidgetTemplate, 'w').write('''\
  ... <input type="text" name="" value=""
  ...        tal:attributes="id view/name; name view/name; value view/value;" />\
  ... ''')

  >>> from z3c.form.widget import WidgetTemplateFactory
  >>> factory = WidgetTemplateFactory(
  ...     textWidgetTemplate, widget=widget.Widget)

  >>> from z3c.form import interfaces
  >>> age.mode is interfaces.INPUT_MODE
  True

  >>> import zope.component
  >>> zope.component.provideAdapter(factory, name=interfaces.INPUT_MODE)

Now for the magic.  We can attach an event to this widget by adapting
it to ``IJSEventWidget``.

  >>> def ageClickHandler():
  ...     return 'alert("This Widget was Clicked!");'

  >>> jsinterfaces.IJSEventWidget(age).addEvent(jsevent.CLICK, ageClickHandler)

Now we can update and render this widget.

  >>> age.update()
  >>> print age.render()
  <input type="text" name="age" value="39" />

If we render the widget in the regular way, nothing is different.
However, we can render it using the IJSEventWidget adapter to have the
event attached.

  >>> jsinterfaces.IJSEventWidget(age).render()
  <input type="text" id="age" name="age" value="39" />
  <script type="javascript">
    $('#age').bind("click", function(){alert("This Widget was Clicked!");});
  </script>


Rendering Widgets with Attached Events
--------------------------------------

There is an easier way to render a bunch of widgets at a time to have
events hooked up to them.  This involves adapting the widget manager
to IJSEventWidgetManager.

Here we will create an interface for which we want to have a form.

  >>> import zope.interface
  >>> import zope.schema
  >>> class IPerson(zope.interface.Interface):
  ...
  ...     name = zope.schema.TextLine(
  ...         title=u'Name',
  ...         required=True)
  ...
  ...     gender = zope.schema.Choice(
  ...         title=u'Gender',
  ...         values=('male', 'female'),
  ...         required=False)
  ...
  ...     age = zope.schema.Int(
  ...         title=u'Age',
  ...         description=u"The person's age.",
  ...         min=0,
  ...         default=20,
  ...         required=False)


  >>> class PersonAddForm(form.AddForm):
  ...
  ...     fields = field.Fields(IPerson)
  ...     prefix = "form"
  ...     def create(self, data):
  ...         return Person(**data)
  ...
  ...     def add(self, object):
  ...         self.context[object.name] = object
  ...
  ...     def nextURL(self):
  ...         return 'index.html'
  ...
  ...     @eventHandler('age')
  ...     def ageClickEvent(self):
  ...         return 'alert("The Age was Clicked!");'
  ...
  ...     @eventHandler('gender', event=jsevent.CHANGED)
  ...     def genderChangeEvent(self):
  ...         return 'alert("The Gender was Changed!");'


Now we can update this form and render the widget event handler.

  >>> request = TestRequest()
  >>> add = PersonAddForm(root, request)
  >>> add.update()

  >>> jsinterfaces.IJSEventWidgetManager(add.widgets).renderEvents()
  <script type="javascript">
    $("#form-age").bind("click", function(){alert("The Age was Clicked!");});
    $("#form-gender").bind("dblclick", function(){alert("The Gender was Changed!");});
  </script>
