================
Spreadsheet Demo
================

The purpose of the spreadsheet demo is to demonstrate how the form framework
can be combined with another framework, in our case the Zope Corp.'s tables.

To start, we need to open a browser and go to the demo applications overview
screen:

  >>> from z3c.formdemo import testing
  >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
  >>> user = ExtendedTestBrowser()
  >>> user.addHeader('Accept-Language', 'en')
  >>> user.open('http://localhost:8080')

Since all demos are purely public, there is no need to log in. Let's now click
on the "Spreadsheet" link:

  >>> user.getLink('Spreadsheet').click()

There is only one screen for this demo. In it you see the candidate
evaluations table:

  >>> testing.printElement(user, "//h1")
  <h1>Spreadsheet Demo ...</h1>

Initially there are no evaluations, so the screen contains little
information. Let's first fill out a few evaluations by clicking on the button
below the table.

  >>> user.getControl('Add').click()

Once clicked, the button below the table disappears, and a new row is shown in
the table allowing us to add another evaluation. So let's fill out information
and add the evaluation:

  >>> user.getControl(name='add.widgets.lastName').value = u'Richter'
  >>> user.getControl(name='add.widgets.firstName').value = u'Stephan'
  >>> user.getControl(name='add.widgets.rating:list').getControl('good').click()

  >>> user.getControl('Add').click()

When the page returns, we see a row with the entry of Stephan Richter, ...

  >>> testing.printElement(user, "//table/tbody/tr[2]")
  <tr class="even"><td class="sorted-on">
      <span id="candidate-0-widgets-lastName"
            class="text-widget required textline-field">Richter</span>
    </td>
    <td class="">
      <span id="candidate-0-widgets-firstName"
            class="text-widget required textline-field">Stephan</span>
    </td>
    <td class="">
      <span id="candidate-0-widgets-rating"
            class="select-widget choice-field"><span
        class="selected-option">good</span></span>
    </td>
    <td class="">
      <input type="submit" ... value="Edit" /></td>
  </tr>

... but also another add evaluation row. This is by design, so that the user
can quickly record new entries. So let's add another:

  >>> user.getControl(name='add.widgets.lastName').value = u'Ineichen'
  >>> user.getControl(name='add.widgets.firstName').value = u'Roger'
  >>> user.getControl(name='add.widgets.rating:list')\
  ...     .getControl('excellent').click()

  >>> user.getControl('Add').click()

We are done now with adding new evaluations. Clicking on the "Cancel" button,
removes the add line.

  >>> user.getControl('Cancel').click()
  >>> user.getControl(name='add.widgets.lastName')
  Traceback (most recent call last):
  ...
  LookupError: name 'add.widgets.lastName'

We can now edit an evaluation by clicking on the row's edit button:

  >>> user.getControl('Edit', index=1).click()

An edit form for this row appears now for Stephan. Let's change his rating to
"average":

  >>> user.getControl(name='candidate-0.widgets.rating:list')\
  ...     .getControl('average').click()

But hitting the "Cancel" button wil ignore the changes and simply return to
diaplay the row:

  >>> user.getControl('Cancel').click()
  >>> testing.printElement(user, "//table/tbody/tr[2]/td[3]/span/span/text()",
  ...                      serialize=False)
  good

Let's now edit the rating for real:

  >>> user.getControl('Edit', index=1).click()
  >>> user.getControl(name='candidate-0.widgets.rating:list')\
  ...     .getControl('average').click()
  >>> user.getControl('Save').click()

Saving the changes also collapses the edit form back into a display form,
saving the user from accessive button clicking. Of course, the data is
properly stored.

  >>> testing.printElement(user, "//table/tbody/tr[2]/td[3]/span/span/text()",
  ...                      serialize=False)
  average

The real power of integrating the forms into ``zc.table`` is the automtic
column sorting feature that comes with the table framework. By default they
are sorted by last name:

  >>> testing.printElement(user, "//table/tbody/tr/td[1]/span/text()",
  ...                      multiple=True, serialize=False)
  Ineichen
  Richter

Clicking on the "Last Name" table header cell, will leave the order, since the
ordering must be initialized. The second time the order is reversed:

  >>> user.getLink('Last Name').click()
  >>> user.getLink('Last Name').click()

  >>> testing.printElement(user, "//table/tbody/tr/td[1]/span/text()",
  ...                      multiple=True, serialize=False)
  Richter
  Ineichen

Selecting another header will sort on it. Let's choose the first name;
clicking on it once sorts it in ascending order:

  >>> user.getLink('First Name').click()
  >>> testing.printElement(user, "//table/tbody/tr/td[2]/span/text()",
  ...                      multiple=True, serialize=False)
  Roger
  Stephan

Clicking it again, reverses the order:

  >>> user.getLink('First Name').click()
  >>> testing.printElement(user, "//table/tbody/tr/td[2]/span/text()",
  ...                      multiple=True, serialize=False)
  Stephan
  Roger

Except for the "Actions" column, all headers can be sorted on:

  >>> user.getLink('Last Name')
  <Link text='Last Name' url='...lastName'>
  >>> user.getLink('First Name')
  <Link text='First Name' url='...firstName'>
  >>> user.getLink('Rating')
  <Link text='Rating' url='...rating'>
  >>> user.getLink('Actions')
  Traceback (most recent call last):
  ...
  LinkNotFoundError
