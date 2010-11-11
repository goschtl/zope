=====================
Date Selection Widget
=====================

The ``DateSelectWidget`` widget provides three select boxes presenting the
day, month and year.

First we have to create a field and a request. Note that we can set the
year range in this widget:

  >>> import datetime
  >>> from z3c.schema.dateselect import DateSelect
  >>> from z3c.widget.dateselect.browser import DateSelectWidget

  >>> field = DateSelect(
  ...     title=u'Birthday',
  ...     description=u'Somebodys birthday',
  ...     yearRange=range(1930, 2007),
  ...     required=True)
  >>> field.__name__ = 'field'

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

Now we can initialize widget.

  >>> widget = DateSelectWidget(field, request)

Let's make sure that all fields have the correct value:

  >>> widget.name
  'field.field'

  >>> widget.label
  u'Birthday'

  >>> widget.hint
  u'Somebodys birthday'

  >>> widget.visible
  True

  >>> widget.required
  True

The constructor should have also created 3 widgets:

  >>> widget.widgets['year']
  <z3c.widget.dateselect.browser.DropdownWidget object at ...>
  >>> widget.widgets['month']
  <z3c.widget.dateselect.browser.DropdownWidget object at ...>
  >>> widget.widgets['day']
  <z3c.widget.dateselect.browser.DropdownWidget object at ...>

let's also test the year range:

  >>> '1929' in widget.widgets['year'].vocabulary.by_token.keys()
  False
  >>> '1930' in widget.widgets['year'].vocabulary.by_token.keys()
  True
  >>> '2006' in widget.widgets['year'].vocabulary.by_token.keys()
  True
  >>> '2007' in widget.widgets['year'].vocabulary.by_token.keys()
  False

Test another year range:

  >>> field2 = DateSelect(
  ...     title=u'Another Birthday',
  ...     yearRange=range(2000, 2010))
  >>> field2.__name__ = 'field'
  >>> widget2 = DateSelectWidget(field2, request)

  >>> '1930' in widget2.widgets['year'].vocabulary.by_token.keys()
  False
  >>> '2000' in widget2.widgets['year'].vocabulary.by_token.keys()
  True
  >>> '2009' in widget2.widgets['year'].vocabulary.by_token.keys()
  True
  >>> '2010' in widget2.widgets['year'].vocabulary.by_token.keys()
  False


``setRenderedValue(value)`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first method is ``setRenderedValue()``. The widget has two use cases,
based on the type of value. If the value is a custom score system, it will
send the information to the custom, min and max widget:

  >>> widget = DateSelectWidget(field, request)
  >>> year = 2000
  >>> month = 12
  >>> day = 31
  >>> data = datetime.date(year, month, day)
  >>> widget.setRenderedValue(data)

  >>> 'value="2000"' in widget()
  True
  >>> 'value="12"' in widget()
  True
  >>> 'value="31"' in widget()
  True


``setPrefix(prefix)`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The prefix determines the name of the widget and all its sub-widgets.

  >>> widget.name
  'field.field'
  >>> widget.widgets['year'].name
  'field.field.year'
  >>> widget.widgets['month'].name
  'field.field.month'
  >>> widget.widgets['day'].name
  'field.field.day'

  >>> widget.setPrefix('test.')

  >>> widget.name
  'test.field'
  >>> widget.widgets['year'].name
  'test.field.year'
  >>> widget.widgets['month'].name
  'test.field.month'
  >>> widget.widgets['day'].name
  'test.field.day'

If the prefix does not end in a dot, one is added:

  >>> widget.setPrefix('test')

  >>> widget.name
  'test.field'
  >>> widget.widgets['year'].name
  'test.field.year'
  >>> widget.widgets['month'].name
  'test.field.month'
  >>> widget.widgets['day'].name
  'test.field.day'


``getInputValue()`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~

This method returns a date object:

  >>> request = TestRequest(form={
  ...     'field.field.year': '2006',
  ...     'field.field.month': '2',
  ...     'field.field.day': '24'})

  >>> widget = DateSelectWidget(field, request)

  >>> value = widget.getInputValue()
  >>> value.year
  2006
  >>> value.month
  2
  >>> value.day
  24

If a set of values does not produce a valid date object, a value error is
raised:

  >>> request = TestRequest(form={
  ...     'field.field.year': '2006',
  ...     'field.field.month': '2',
  ...     'field.field.day': '29'})

  >>> widget = DateSelectWidget(field, request)
  >>> widget.getInputValue()
  Traceback (most recent call last):
  ...
  WidgetInputError: ('field', u'Birthday', u'day is out of range for month')

  >>> widget._error.__class__
  <class 'zope.formlib.interfaces.WidgetInputError'>


``applyChanges(content)`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method applies the new date to the passed content. However, it
must be smart enough to detect whether the values really changed.

  >>> class Content(object):
  ...     field = None
  >>> content = Content()

  >>> request = TestRequest(form={
  ...     'field.field.year': '2006',
  ...     'field.field.month': '2',
  ...     'field.field.day': '24'})

  >>> widget = DateSelectWidget(field, request)
  >>> widget.applyChanges(content)
  True
  >>> content.field
  datetime.date(2006, 2, 24)

  >>> widget.applyChanges(content)
  False


``hasInput()`` Method
~~~~~~~~~~~~~~~~~~~~~

This method checks for any input, but does not validate it.

  >>> request = TestRequest()
  >>> widget = DateSelectWidget(field, request)
  >>> widget.hasInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.year': '2006'})
  >>> widget = DateSelectWidget(field, request)
  >>> widget.hasInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.month': '2'})
  >>> widget = DateSelectWidget(field, request)
  >>> widget.hasInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.day': '24'})
  >>> widget = DateSelectWidget(field, request)
  >>> widget.hasInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.year': '2006',
  ...     'field.field.month': '2',
  ...     'field.field.day': '24'})
  >>> widget = DateSelectWidget(field, request)
  >>> widget.hasInput()
  True


``hasValidInput()`` Method
~~~~~~~~~~~~~~~~~~~~~~~~~~

Additionally to checking for any input, this method also checks whether the
input is valid:

  >>> request = TestRequest()
  >>> widget = DateSelectWidget(field, request)
  >>> widget.hasValidInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.year': '2006'})
  >>> widget = DateSelectWidget(field, request)
  >>> widget.hasValidInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.month': '2'})
  >>> widget = DateSelectWidget(field, request)
  >>> widget.hasValidInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.day': '24'})
  >>> widget = DateSelectWidget(field, request)
  >>> widget.hasValidInput()
  False

  >>> request = TestRequest(form={
  ...     'field.field.year': '2006',
  ...     'field.field.month': '2',
  ...     'field.field.day': '24'})
  >>> widget = DateSelectWidget(field, request)
  >>> widget.hasValidInput()
  True


``hidden()`` Method
~~~~~~~~~~~~~~~~~~~

This method is renders the output as hidden fields:

  >>> request = TestRequest(form={
  ...     'field.field.year': '2006',
  ...     'field.field.month': '2',
  ...     'field.field.day': '24'})
  >>> widget = DateSelectWidget(field, request)
  >>> print widget.hidden()
  <input class="hiddenType" id="field.field.year" name="field.field.year"
         type="hidden" value="2006" />
  <input class="hiddenType" id="field.field.month" name="field.field.month"
         type="hidden" value="2"  />
  <input class="hiddenType" id="field.field.day" name="field.field.day"
         type="hidden" value="24"  />


``error()`` Method
~~~~~~~~~~~~~~~~~~

Let's test some bad data and check the error handling.

The day field contains an invalid value:

  >>> request = TestRequest(form={
  ...     'field.field.year': '2006',
  ...     'field.field.month': '2',
  ...     'field.field.day': '99'})
  >>> widget = DateSelectWidget(field, request)
  >>> widget.getInputValue()
  Traceback (most recent call last):
  ...
  ConversionError: (u'Invalid value', InvalidValue("token '99' not found in vocabulary"))
  >>> print widget.error()
  <span class="error">Invalid value</span>

The month field contains an invalid value:

  >>> request = TestRequest(form={
  ...     'field.field.year': '2006',
  ...     'field.field.month': '0',
  ...     'field.field.day': '31'})
  >>> widget = DateSelectWidget(field, request)
  >>> widget.getInputValue()
  Traceback (most recent call last):
  ...
  ConversionError: (u'Invalid value', InvalidValue("token '0' not found in vocabulary"))
  >>> print widget.error()
  <span class="error">Invalid value</span>

The year field contains an invalid value:

  >>> request = TestRequest(form={
  ...     'field.field.year': '1900',
  ...     'field.field.month': '1',
  ...     'field.field.day': '31'})
  >>> widget = DateSelectWidget(field, request)
  >>> widget.getInputValue()
  Traceback (most recent call last):
  ...
  ConversionError: (u'Invalid value', InvalidValue("token '1900' not found in vocabulary"))
  >>> print widget.error()
  <span class="error">Invalid value</span>

The single inputs were correct, but did not create a valid date.

  >>> request = TestRequest(form={
  ...     'field.field.year': '1980',
  ...     'field.field.month': '2',
  ...     'field.field.day': '31'})
  >>> widget = DateSelectWidget(field, request)
  >>> widget.getInputValue()
  Traceback (most recent call last):
  ...
  WidgetInputError: ('field', u'Birthday', u'day is out of range for month')

  >>> print widget.error()
  <span class="error">day is out of range for month</span>

No error occurred:

  >>> request = TestRequest(form={
  ...     'field.field.year': '1980',
  ...     'field.field.month': '1',
  ...     'field.field.day': '31'})
  >>> widget = DateSelectWidget(field, request)
  >>> widget.getInputValue()
  datetime.date(1980, 1, 31)
  >>> widget.error()
  ''


``__call__()`` Method
~~~~~~~~~~~~~~~~~~~~~

This method renders the widget using the sub-widgets. Let's see the output:

  >>> request = TestRequest(form={
  ...     'field.field.year': '2006',
  ...     'field.field.month': '2',
  ...     'field.field.day': '24'})
  >>> widget = DateSelectWidget(field, request)
  >>> print widget()
  <select id="field.field.day" name="field.field.day" size="1" >
  <option value="1">1</option>
  ...
  <option value="23">23</option>
  <option selected="selected" value="24">24</option>
  <option value="25">25</option>
  ...
  <option value="31">31</option>
  </select><input name="field.field.day-empty-marker" type="hidden"
                  value="1" />&nbsp;
  <select id="field.field.month" name="field.field.month" size="1" >
  <option value="1">1</option>
  <option selected="selected" value="2">2</option>
  <option value="3">3</option>
  ...
  <option value="12">12</option>
  </select><input name="field.field.month-empty-marker" type="hidden"
                  value="1" />&nbsp;
  <select id="field.field.year" name="field.field.year" size="1" >
  <option value="1930">1930</option>
  ...
  <option value="2005">2005</option>
  <option selected="selected" value="2006">2006</option>
  </select><input
      name="field.field.year-empty-marker" type="hidden" value="1" />
  <BLANKLINE>
