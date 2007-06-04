==========
z3c.formjs
==========

The z3c.formjs package provides additional support for javascript and
ajax for the z3c.form package.


Buttons
=======

z3c.form defines buttons that always submit forms.  It is also highly
useful to have buttons in your form that modify that perform a client
side action using javascript.  z3c.formjs.button provides buttons with
javascript event hooks.

  >>> from.z3c.formjs import jsbutton

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
  >>> from z3c.formjs import interfaces as jsinterfaces
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
  ...     @jsbutton.handler(IButtons['cancel'])
  ...     def cancel(self, action):
  ...         return 'alert("You Clicked the Cancel Button!");'

Now we can create the button action manager just as we do with regular
buttons

Let' now create an action manager for the button manager in the form. To do
that we first need a request and a form instance:

  >>> from z3c.form.testing import TestRequest
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

  >>> from z3c.formjs import testing as jstesting,
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
         name="form.buttons.apply" class="submitWidget"
         value="Apply"
         onClick="alert("You Clicked the Apply Button!");"/>

