===============
US Phone Widget
===============

The US phone number widget can be used as a custom widget for text line
fields, enforcing a particular layout.

First we have to create a field and a request:

  >>> import datetime
  >>> import zope.schema

  >>> field = zope.schema.TextLine(
  ...     title=u'Phone',
  ...     description=u'Phone Number',
  ...     required=True)
  >>> field.__name__ = 'field'

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

Now we can initialize widget.

  >>> from z3c.widget.usphone.browser import PhoneWidget
  >>> widget = PhoneWidget(field, request)

Let's make sure that all fields have the correct value:

  >>> widget.name
  'field.field'

  >>> widget.label
  u'Phone'

  >>> widget.hint
  u'Phone Number'

  >>> widget.visible
  True

  >>> widget.required
  True

The constructor should have also created 3 sub-widgets:

  >>> widget.widgets['first']
  <zope.formlib.textwidgets.TextWidget object at ...>
  >>> widget.widgets['second']
  <zope.formlib.textwidgets.TextWidget object at ...>
  >>> widget.widgets['third']
  <zope.formlib.textwidgets.TextWidget object at ...>


``setRenderedValue(value)`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first method is ``setRenderedValue()``. The widget has two use cases,
based on the type of value:

  >>> widget = PhoneWidget(field, request)
  >>> widget.setRenderedValue(u'123-456-7890')
  >>> print widget()
  (<input class="textType" id="field.field.first" name="field.field.first"
          size="3" type="text" value="123"  />)&nbsp;
  <input class="textType" id="field.field.second" name="field.field.second"
         size="3" type="text" value="456"  />&nbsp;&mdash;&nbsp;
  <input class="textType" id="field.field.third" name="field.field.third"
         size="4" type="text" value="7890"  />


``setPrefix(prefix)`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The prefix determines the name of the widget and all its sub-widgets.

  >>> widget.name
  'field.field'
  >>> widget.widgets['first'].name
  'field.field.first'
  >>> widget.widgets['second'].name
  'field.field.second'
  >>> widget.widgets['third'].name
  'field.field.third'

  >>> widget.setPrefix('test.')

  >>> widget.name
  'test.field'
  >>> widget.widgets['first'].name
  'test.field.first'
  >>> widget.widgets['second'].name
  'test.field.second'
  >>> widget.widgets['third'].name
  'test.field.third'

If the prefix does not end in a dot, one is added:

  >>> widget.setPrefix('test')

  >>> widget.name
  'test.field'
  >>> widget.widgets['first'].name
  'test.field.first'
  >>> widget.widgets['second'].name
  'test.field.second'
  >>> widget.widgets['third'].name
  'test.field.third'


``getInputValue()`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~

This method returns the full phone string:

  >>> request = TestRequest(form={
  ...     'field.field.first': '123',
  ...     'field.field.second': '456',
  ...     'field.field.third': '7890'})

  >>> widget = PhoneWidget(field, request)

  >>> value = widget.getInputValue()
  >>> value
  u'123-456-7890'

If a set of values does not produce a valid string, a value error is
raised:

  >>> request = TestRequest(form={
  ...     'field.field.first': '1234',
  ...     'field.field.second': '56',
  ...     'field.field.third': '7890'})

  >>> widget = PhoneWidget(field, request)
  >>> widget.getInputValue()
  Traceback (most recent call last):
  ...
  WidgetInputError: ('first', u'Area Code', ConstraintNotSatisfied(u'1234'))

  >>> widget._error.__class__
  <class 'zope.formlib.interfaces.WidgetInputError'>


``applyChanges(content)`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method applies the new phone number to the passed content. However, it
must be smart enough to detect whether the values really changed.

  >>> class Content(object):
  ...     field = None
  >>> content = Content()

  >>> request = TestRequest(form={
  ...     'field.field.first': '123',
  ...     'field.field.second': '456',
  ...     'field.field.third': '7890'})

  >>> widget = PhoneWidget(field, request)
  >>> widget.applyChanges(content)
  True
  >>> content.field
  u'123-456-7890'

  >>> widget.applyChanges(content)
  False


``hasInput()`` Method
~~~~~~~~~~~~~~~~~~~~~

This method checks for any input, but does not validate it.

  >>> request = TestRequest()
  >>> widget = PhoneWidget(field, request)
  >>> widget.hasInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.first': '123'})
  >>> widget = PhoneWidget(field, request)
  >>> widget.hasInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.second': '456'})
  >>> widget = PhoneWidget(field, request)
  >>> widget.hasInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.third': '7890'})
  >>> widget = PhoneWidget(field, request)
  >>> widget.hasInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.first': '123',
  ...     'field.field.second': '456',
  ...     'field.field.third': '7890'})
  >>> widget = PhoneWidget(field, request)
  >>> widget.hasInput()
  True


``hasValidInput()`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~

Additionally to checking for any input, this method also checks whether the
input is valid:

  >>> request = TestRequest()
  >>> widget = PhoneWidget(field, request)
  >>> widget.hasValidInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.first': '123'})
  >>> widget = PhoneWidget(field, request)
  >>> widget.hasValidInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.second': '456'})
  >>> widget = PhoneWidget(field, request)
  >>> widget.hasValidInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.third': '7890'})
  >>> widget = PhoneWidget(field, request)
  >>> widget.hasValidInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.first': '123',
  ...     'field.field.second': '456',
  ...     'field.field.third': '7890'})
  >>> widget = PhoneWidget(field, request)
  >>> widget.hasValidInput()
  True


``hidden()`` Method
~~~~~~~~~~~~~~~~~~~

This method is renders the output as hidden fields:

  >>> request = TestRequest(form={
  ...     'field.field.first': '123',
  ...     'field.field.second': '456',
  ...     'field.field.third': '7890'})
  >>> widget = PhoneWidget(field, request)
  >>> print widget.hidden()
  <input class="hiddenType" id="field.field.first" name="field.field.first"
         type="hidden" value="123" />
  <input class="hiddenType" id="field.field.second" name="field.field.second"
         type="hidden" value="456"  />
  <input class="hiddenType" id="field.field.third" name="field.field.third"
         type="hidden" value="7890"  />


``error()`` Method
~~~~~~~~~~~~~~~~~~

Let's test some bad data and check the error handling.

The third field contains an invalid value:

  >>> request = TestRequest(form={
  ...     'field.field.first': '123',
  ...     'field.field.second': '456',
  ...     'field.field.third': '78901'})
  >>> widget = PhoneWidget(field, request)
  >>> widget.getInputValue()
  Traceback (most recent call last):
  ...
  WidgetInputError: ('third', u'Four Digits', ConstraintNotSatisfied(u'78901'))

  >>> print widget.error()
  <span class="error">Constraint not satisfied</span>

The second field contains an invalid value:

  >>> request = TestRequest(form={
  ...     'field.field.first': '123',
  ...     'field.field.second': '45-',
  ...     'field.field.third': '7890'})
  >>> widget = PhoneWidget(field, request)
  >>> widget.getInputValue()
  Traceback (most recent call last):
  ...
  WidgetInputError: ('second', u'Three Digits', ConstraintNotSatisfied(u'45-'))

  >>> print widget.error()
  <span class="error">Constraint not satisfied</span>

The first field contains an invalid value:

  >>> request = TestRequest(form={
  ...     'field.field.first': 'xxx',
  ...     'field.field.second': '456',
  ...     'field.field.third': '7890'})
  >>> widget = PhoneWidget(field, request)
  >>> widget.getInputValue()
  Traceback (most recent call last):
  ...
  WidgetInputError: ('first', u'Area Code', ConstraintNotSatisfied(u'xxx'))

  >>> print widget.error()
  <span class="error">Constraint not satisfied</span>

No error occurred:

  >>> request = TestRequest(form={
  ...     'field.field.first': '123',
  ...     'field.field.second': '456',
  ...     'field.field.third': '7890'})
  >>> widget = PhoneWidget(field, request)
  >>> widget.getInputValue()
  u'123-456-7890'
  >>> widget.error()
  ''


``__call__()`` Method
~~~~~~~~~~~~~~~~~~~~~

This method renders the widget using the sub-widgets. Let's see the output:

  >>> request = TestRequest(form={
  ...     'field.field.first': '123',
  ...     'field.field.second': '456',
  ...     'field.field.third': '7890'})
  >>> widget = PhoneWidget(field, request)
  >>> print widget()
  (<input class="textType" id="field.field.first" name="field.field.first"
          size="3" type="text" value="123"  />)&nbsp;
  <input class="textType" id="field.field.second" name="field.field.second"
         size="3" type="text" value="456"  />&nbsp;&mdash;&nbsp;
  <input class="textType" id="field.field.third" name="field.field.third"
         size="4" type="text" value="7890"  />
