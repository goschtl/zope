DropDownDateWidget
==================

  >>> from z3c.widget.dropdowndatewidget.widget import DropDownDateWidget

  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()

Widgets are use for fields.

  >>> from zope.schema import Date
  >>> dateField = Date(__name__='foo', title=u'Foo')

  >>> widget = DropDownDateWidget(dateField, request)

  >>> widget.name
  'field.foo'
  >>> widget.label
  u'Foo'
  >>> widget.hasInput()
  False

We need to provide some input.

  >>> request.form['field.foo.day'] = '1'
  >>> widget.hasInput()
  False
  >>> request.form['field.foo.month'] = '6'
  >>> widget.hasInput()
  False
  >>> request.form['field.foo.year'] = '1963'
  >>> widget.hasInput()
  True

Read the value.

  >>> widget.getInputValue()
  datetime.date(1963, 6, 1)

Let's render the widget.

  >>> print widget()
  <div class="dropDownDateWidget"><select class="dayField" id="field.foo.day" name="field.foo.day">...</select>
  <select class="monthField" id="field.foo.month" name="field.foo.month">...</select>
  <select class="yearField" id="field.foo.year" name="field.foo.year">...</select>
  </div>

And if we set a value.

  >>> from datetime import date
  >>> widget.setRenderedValue(date(1977, 4, 3))
  >>> print widget()
  <div class="dropDownDateWidget"><select ...<option selected="selected" value="03">...
  <select ...<option selected="selected" value="04">...
  <select ...<option selected="selected" value="1977">...
  ...

