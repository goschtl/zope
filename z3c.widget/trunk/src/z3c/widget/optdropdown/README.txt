=========================
Optional Dropdown Widgets
=========================

The Optional Dropdown Widget simulates the common desktop widget of a combo
box, which can also receive a custom entry.

Before we can start, we have to do a little bit of setup:

  >>> import zope.component
  >>> import zope.schema
  >>> import zope.app.form.browser
  >>> from zope.publisher.interfaces.browser import IBrowserRequest

  >>> zope.component.provideAdapter(
  ...     zope.app.form.browser.TextWidget,
  ...     (zope.schema.interfaces.ITextLine, IBrowserRequest),
  ...     zope.app.form.interfaces.IInputWidget)


First we have to create a field and a request:

  >>> from z3c.schema.optchoice import OptionalChoice

  >>> optchoice = OptionalChoice(
  ...     __name__='occupation',
  ...     title=u'Occupation',
  ...     description=u'The Occupation',
  ...     values=(u'Programmer', u'Designer', u'Project Manager'),
  ...     value_type=zope.schema.TextLine())

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

Now we can initialize widget.

  >>> class Content(object):
  ...     occupation = None
  >>> content = Content()
  >>> boundOptChoice = optchoice.bind(content)

  >>> from z3c.widget.optdropdown import OptionalDropdownWidget
  >>> widget = OptionalDropdownWidget(boundOptChoice, request)

Let's make sure that all fields have the correct value:

  >>> widget.name
  'field.occupation'

  >>> widget.label
  u'Occupation'

  >>> widget.hint
  u'The Occupation'

  >>> widget.visible
  True

  >>> widget.required
  True

The constructor should have also created 2 widgets:

  >>> widget.customWidget
  <zope.formlib.textwidgets.TextWidget object at ...>
  >>> widget.dropdownWidget
  <zope.formlib.itemswidgets.DropdownWidget object at ...>


``setRenderedValue(value)`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first method is ``setRenderedValue()``. The widget has two use cases,
based on the type of value. If the value is a custom value, it will
send the information to the custom widget:

  >>> print widget.customWidget()
  <... value="" />
  >>> 'selected=""' in widget.dropdownWidget()
  False

  >>> widget.setRenderedValue(u'Scientist')

  >>> print widget.customWidget()
  <... value="Scientist" />
  >>> 'selected=""' in widget.dropdownWidget()
  False

After resetting the widget passing in one of the choices in the
vocabulary, the value should be displayed in the dropdown:

  >>> widget.setRenderedValue(u'Designer')

  >>> print widget.customWidget()
  <... value="" />
  >>> print widget.dropdownWidget()
  <div>
  ...
  <option selected="selected" value="Designer">Designer</option>
  ...
  </div>


``setPrefix(prefix)`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The prefix determines the name of the widget and the sub-widgets.

  >>> widget.name
  'field.occupation'
  >>> widget.dropdownWidget.name
  'field.occupation.occupation'
  >>> widget.customWidget.name
  'field.occupation.custom'

  >>> widget.setPrefix('test.')

  >>> widget.name
  'test.occupation'
  >>> widget.dropdownWidget.name
  'test.occupation.occupation'
  >>> widget.customWidget.name
  'test.occupation.custom'


``getInputValue()`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~

This method returns a value based on the input; the data is assumed to
be valid. In our case that means, if we entered a custom value, it is
returned:

  >>> request = TestRequest(form={
  ...     'field.occupation.custom': u'Teacher'})

  >>> widget = OptionalDropdownWidget(boundOptChoice, request)

  >>> widget.getInputValue()
  u'Teacher'

On the other hand, if we selected a choice from the vocabulary, it should be
returned:

  >>> request = TestRequest(form={
  ...     'field.occupation.occupation': u'Designer'})

  >>> widget = OptionalDropdownWidget(boundOptChoice, request)

  >>> widget.getInputValue()
  u'Designer'


``applyChanges(content)`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method applies the new value to the passed content. However, it
must be smart enough to detect whether the values really changed.

  >>> request = TestRequest(form={
  ...     'field.occupation.custom': u'Teacher'})

  >>> widget = OptionalDropdownWidget(boundOptChoice, request)
  >>> widget.applyChanges(content)
  True
  >>> content.occupation
  u'Teacher'

  >>> widget.applyChanges(content)
  False

  >>> request = TestRequest(form={
  ...     'field.occupation.occupation': u'Designer'})

  >>> widget = OptionalDropdownWidget(boundOptChoice, request)

  >>> widget.applyChanges(content)
  True
  >>> content.occupation
  u'Designer'

  >>> widget.applyChanges(content)
  False


``hasInput()`` Method
~~~~~~~~~~~~~~~~~~~~~

This mehtod checks for any input, but does not validate it. In our case this
means that either a choice has been selected or the the custom value has been
entered.

  >>> request = TestRequest()
  >>> widget = OptionalDropdownWidget(boundOptChoice, request)
  >>> widget.hasInput()
  False

  >>> request = TestRequest(form={
  ...     'field.occupation.custom': u'Teacher\nBad Stuff'})
  >>> widget = OptionalDropdownWidget(boundOptChoice, request)
  >>> widget.hasInput()
  True

  >>> request = TestRequest(form={
  ...     'field.occupation.occupation': u'Waitress'})
  >>> widget = OptionalDropdownWidget(boundOptChoice, request)
  >>> widget.hasInput()
  True


``hasValidInput()`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~

Additionally to checking for any input, this method also checks whether the
input is valid:

  >>> request = TestRequest()
  >>> widget = OptionalDropdownWidget(boundOptChoice, request)
  >>> widget.hasValidInput()
  False

  >>> request = TestRequest(form={
  ...     'field.occupation.occupation': u'Waitress'})
  >>> widget = OptionalDropdownWidget(boundOptChoice, request)
  >>> widget.hasValidInput()
  False

  >>> request = TestRequest(form={
  ...     'field.occupation.occupation': u'Designer'})
  >>> widget = OptionalDropdownWidget(boundOptChoice, request)
  >>> widget.hasValidInput()
  True

  >>> request = TestRequest(form={
  ...     'field.occupation.custom': u'Teacher\nBad Stuff'})
  >>> widget = OptionalDropdownWidget(boundOptChoice, request)
  >>> widget.hasValidInput()
  False

  >>> request = TestRequest(form={
  ...     'field.occupation.custom': u'Teacher'})
  >>> widget = OptionalDropdownWidget(boundOptChoice, request)
  >>> widget.hasValidInput()
  True


hidden() Method
~~~~~~~~~~~~~~~

This method is implemented by simply concatenating the two widget's hidden
output:

  >>> request = TestRequest()
  >>> widget = OptionalDropdownWidget(boundOptChoice, request)
  >>> widget.setRenderedValue(u'Designer')
  >>> print widget.hidden()
  <input class="hiddenType" id="field.occupation.occupation"
         name="field.occupation.occupation" type="hidden" value="Designer"  />
  <input class="hiddenType" id="field.occupation.custom"
         name="field.occupation.custom" type="hidden" value=""  />

  >>> widget.setRenderedValue(u'Teacher')
  >>> print widget.hidden()
  <input class="hiddenType" id="field.occupation.occupation"
         name="field.occupation.occupation" type="hidden" value=""  />
  <input class="hiddenType" id="field.occupation.custom"
         name="field.occupation.custom" type="hidden" value="Teacher"  />


error() Method
~~~~~~~~~~~~~~

Again, we have our two cases. If an error occured in the dropdown, it is
reported:

  >>> from zope.app.form.interfaces import IWidgetInputError
  >>> from zope.app.form.browser.exception import WidgetInputErrorView
  >>> from zope.app.form.browser.interfaces import IWidgetInputErrorView

  >>> zope.component.provideAdapter(
  ...     WidgetInputErrorView,
  ...     (IWidgetInputError, IBrowserRequest), IWidgetInputErrorView)

  >>> request = TestRequest(form={
  ...     'field.occupation.occupation': u'Designer'})
  >>> widget = OptionalDropdownWidget(boundOptChoice, request)
  >>> widget.getInputValue()
  u'Designer'
  >>> widget.error()
  ''

  >>> request = TestRequest(form={
  ...     'field.occupation.occupation': u'Waitress'})
  >>> widget = OptionalDropdownWidget(boundOptChoice, request)

  >>> widget.getInputValue()
  Traceback (most recent call last):
  ...
  ConversionError: (u'Invalid value', InvalidValue("token u'Waitress' not found in vocabulary"))
  >>> widget.error()
  u'<span class="error">Invalid value</span>'

Otherwise the custom widget's errors are reported:

  >>> request = TestRequest(form={
  ...     'field.occupation.custom': u'Teacher'})
  >>> widget = OptionalDropdownWidget(boundOptChoice, request)
  >>> widget.getInputValue()
  u'Teacher'
  >>> widget.error()
  ''

  >>> request = TestRequest(form={
  ...     'field.occupation.custom': u'Teacher\nBad Stuff'})
  >>> widget = OptionalDropdownWidget(boundOptChoice, request)

  >>> widget.getInputValue()
  Traceback (most recent call last):
  ...
  WidgetInputError: ('custom', u'', ConstraintNotSatisfied(u'Teacher\nBad Stuff'))
  >>> widget.error()
  u'<span class="error">Constraint not satisfied</span>'


__call__() Method
~~~~~~~~~~~~~~~~~

This method renders the widget using the sub-widgets. It simply adds the two
widgets' output placing the ``connector between them:

  >>> request = TestRequest(form={
  ...     'field.occupation.custom': u'Teacher'})

  >>> widget = OptionalDropdownWidget(boundOptChoice, request)
  >>> widget.connector
  u'<br />\n'

  >>> print widget()
  <div>
  <div class="value">
  <select id="field.occupation.occupation"
          name="field.occupation.occupation" size="1" >
  <option selected="selected" value="">(nothing selected)</option>
  <option value="Programmer">Programmer</option>
  <option value="Designer">Designer</option>
  <option value="Project Manager">Project Manager</option>
  </select>
  </div>
  <input name="field.occupation.occupation-empty-marker" type="hidden"
         value="1" />
  </div><br />
  <input class="textType" id="field.occupation.custom"
         name="field.occupation.custom" size="20" type="text" value="Teacher" />
