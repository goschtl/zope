============
Widgets Demo
============

The purpose of the widgets demo is demonstrate that there exists a widget for
each standard field type and how it works.

To start, we need to open a browser and go to the demo applications overview
screen:

  >>> from z3c.formdemo import testing
  >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
  >>> user = ExtendedTestBrowser()
  >>> user.addHeader('Accept-Language', 'en')
  >>> user.open('http://localhost:8080')

Since all demos are purely public, there is no need to log in. Let's now click
on the "All widgets" link:

  >>> user.getLink('All widgets').click()

You are now in the widgets form. Let's now fill out all forms an submit the
form:

  >>> import cStringIO

  >>> def addSelection(browser, name, value, selected=True):
  ...     form = browser.mech_browser.forms().next()
  ...     form.new_control(
  ...         'select', name, attrs={'__select': {'name': name, 'size': '5'}})
  ...     form.new_control(
  ...         'select', name,
  ...         attrs={'__select': {'name': name, 'size': '5'},
  ...                'selected': 'selected', 'value': value})

  >>> user.getControl('ASCII', index=0).value += u' Add on.'
  >>> user.getControl('ASCII Line').value += u' Add on.'
  >>> user.getControl(name='form.widgets.boolField:list')\
  ...     .getControl(value='false').click() # Boolean
  >>> user.getControl('Bytes', index=0).add_file(
  ...     cStringIO.StringIO('File contents'), 'text/plain', 'test.txt')
  >>> user.getControl('Bytes Line').value += u' Add on.'
  >>> user.getControl('Choice', index=0).getControl('Two').click()
  >>> user.getControl('Choice (Not Required)').getControl('Two').click()
  >>> user.getControl('Choice (Explicit Prompt)').getControl('Two').click()
  >>> user.getControl('Date', index=0).value = u'7/1/07'
  >>> user.getControl('Date/Time').value = u'7/1/07 12:15 AM'
  >>> user.getControl('Decimal').value = u'12439.986'
  >>> user.getControl('Dotted Name').value += u'demo'
  >>> user.getControl('Float').value = u'12439.986'
  >>> user.getControl('Frozen Set').getControl('One').click()
  >>> user.getControl('Id').value += u'demo'
  >>> user.getControl('Integer').value = u'12439'
  >>> addSelection(user, 'form.widgets.listField', u'1')
  >>> user.getControl('Password').value = u'pwd'
  >>> user.getControl('Set', index=1).getControl('One').click()
  >>> user.getControl('Source Text').value += u' Add on.'
  >>> user.getControl('Text', index=1).value += u' Add on.'
  >>> user.getControl('Text Line').value += u' Add on.'
  >>> user.getControl('Time', index=1).value = u'12:15 AM'
  >>> user.getControl('Time Delta').value = u'4 days, 1:00:00'
  >>> addSelection(user, 'form.widgets.tupleField', u'1')
  >>> user.getControl('URI').value += u'/Documentation'
  >>> user.getControl(name='form.widgets.hiddenField').value += u' Add on.'

  >>> user.getControl('Apply').click()

Once submitted, the same form returns with a data changed method:

  >>> from z3c.formdemo import testing
  >>> testing.printElement(user, "//div[@class='summary']")
  <div class="summary">Data successfully updated.</div>

Let's now ensure that the data has been truly uploaded:

  >>> from z3c.formdemo.widgets import interfaces
  >>> fields = interfaces.IAllFields(getRootFolder())

  >>> fields.asciiField
  'This is\r\n ASCII. Add on.'
  >>> fields.asciiLineField
  'An ASCII line. Add on.'
  >>> fields.boolField
  False
  >>> fields.bytesField
  'File contents'
  >>> fields.bytesLineField
  'A Bytes line. Add on.'
  >>> fields.choiceField
  2
  >>> fields.optionalChoiceField
  2
  >>> fields.promptChoiceField
  2
  >>> fields.dateField
  datetime.date(2007, 7, 1)
  >>> fields.datetimeField
  datetime.datetime(2007, 7, 1, 0, 15)
  >>> fields.decimalField
  Decimal("12439.986")
  >>> fields.dottedNameField
  'z3c.formdemo'
  >>> fields.floatField
  12439.986000000001
  >>> fields.frozenSetField
  frozenset([3])
  >>> fields.idField
  'z3c.formdemo'
  >>> fields.intField
  12439
  >>> fields.listField
  [1]
  >>> fields.passwordField
  u'pwd'
  >>> fields.setField
  set([3])
  >>> fields.sourceTextField
  u'<source /> Add on.'
  >>> fields.textField
  u'Some\r\n Text. Add on.'
  >>> fields.textLineField
  u'Some Text line. Add on.'
  >>> fields.timeField
  datetime.time(0, 15)
  >>> fields.timedeltaField
  datetime.timedelta(4, 3600)
  >>> fields.tupleField
  (1,)
  >>> fields.uriField
  'http://zope.org/Documentation'
  >>> fields.hiddenField
  u'Some Hidden Text. Add on.'

We also have an image button, that can be clicked:

  >>> user.getControl(name='form.buttons.pressme').click()
  >>> testing.printElement(user, "//div[@class='summary']")
  <div class="summary">Press me was clicked!</div>
