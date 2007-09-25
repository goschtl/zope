================
Addressbook Demo
================

The purpose of the addressbook demo is to demonstrate a complex, form-driven
UI with several sub-forms and table-integration.

To start, we need to open a browser and go to the demo applications overview
screen:

  >>> from z3c.formdemo import testing
  >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
  >>> user = ExtendedTestBrowser()
  >>> user.addHeader('Accept-Language', 'en')
  >>> user.open('http://localhost:8080')

Since all demos are purely public, there is no need to log in. Let's now click
on the "Address Book" link:

  >>> user.getLink('Address Book').click()

There is only one screen for this demo. In it you see the table of all
contacts on the left side and on the right side is the contact
form. Initially, this is an add form.

  >>> testing.printElement(user, "//h1")
  <h1><span>Address Book Demo</span></h1>

So let's start by filling out the add form. The first portion contains basic
personal information:

  >>> user.getControl('First Name').value = 'Stephan'
  >>> user.getControl('Last Name').value = 'Richter'

  >>> user.getControl(name='contact.add.widgets.birthday.day:list')\
  ...     .getControl('25').click()
  >>> user.getControl(name='contact.add.widgets.birthday.year:list')\
  ...     .getControl('1980').click()

In the second portion we can add any number of addresses. Let's just add a
home address:

  >>> user.getControl('Add', index=0).click()

  >>> user.getControl('Street').value = '110 Main Street'
  >>> user.getControl('City').value = 'Maynard'
  >>> user.getControl('State').value = 'MA'
  >>> user.getControl('ZIP').value = '01754'

You cannot add the same address twice:

  >>> user.getControl('Add', index=0).click()
  >>> testing.printElement(user, "//div[@class='summary']")
  <div class="summary">Address already provided for contact.</div>

When accidently adding another address, ...

  >>> user.getControl(name='contact.add.addresses.widgets.addressName:list')\
  ...     .getControl('Work').click()
  >>> user.getControl('Add', index=0).click()

you can delete it any time:

  >>> user.getControl('Delete', index=1).click()

Let's now add the home phone number, because it is a required field:

  >>> user.getControl(name='contact.add.phones.homePhone.widgets.countryCode')\
  ...     .value = '+1'
  >>> user.getControl(name='contact.add.phones.homePhone.widgets.areaCode')\
  ...     .value = '555'
  >>> user.getControl(name='contact.add.phones.homePhone.widgets.number')\
  ...     .value = '127-1284'

Finally, the user is requested to enter the E-mail addresses of the contact;
we have two in this case:

  >>> user.getControl(name='contact.add.emails.widgets.fullAddress')\
  ...     .value = 'srichter@gmail.com'
  >>> user.getControl('Add', index=1).click()

  >>> user.getControl(name='contact.add.emails.widgets.fullAddress')\
  ...     .value = 'srichter@tufts.edu'
  >>> user.getControl('Add', index=1).click()

Once all the information has been provided, we can add the contact:

  >>> user.getControl('Add Contact').click()

The new contact appears now in the contact list:

  >>> testing.printElement(user, "//table/tbody/tr[1]")
  <tr class="odd"><td class="sorted-on">
      <a href="...?selectContact=contact-0">Richter</a>
    </td>
    <td class="">
      <a href="...?selectContact=contact-0">Stephan</a>
    </td>
  </tr>

By clicking on the name, the edit form for Stephan is shown:

  >>> user.getLink('Richter').click()

Note that the row is highlighted now:

  >>> testing.printElement(user, "//table/tbody/tr[1]")
  <tr class="selected"><td class="sorted-on">
      <a href="...?selectContact=contact-0">Richter</a>
    </td>
    <td class="">
      <a href="...?selectContact=contact-0">Stephan</a>
    </td>
  </tr>

After adding a work phone number and deleting one of the two E-mail addresses,

  >>> user.getControl(name='contact.edit.phones.workPhone.widgets.countryCode')\
  ...     .value = '+1'
  >>> user.getControl(name='contact.edit.phones.workPhone.widgets.areaCode')\
  ...     .value = '555'
  >>> user.getControl(name='contact.edit.phones.workPhone.widgets.number')\
  ...     .value = '346-3573'

  >>> user.getControl('Delete', index=1).click()

we now save the contact changes:

  >>> user.getControl('Apply').click()

This submission saves all the data but stays in the edit form of the
contact. Only by pressing the "Done" button, the add form will return.

  >>> user.getControl('Done').click()
  >>> user.getControl('Add Contact')
  <SubmitControl name='contact.add.buttons.add' type='submit'>

You will also notice that the contact is not highlighted in the table
anymore. Let's nwo add a second contact:

  >>> user.getControl('First Name').value = 'Roger'
  >>> user.getControl('Last Name').value = 'Ineichen'

  >>> user.getControl(name='contact.add.phones.homePhone.widgets.countryCode')\
  ...     .value = '+41'
  >>> user.getControl(name='contact.add.phones.homePhone.widgets.areaCode')\
  ...     .value = '43'
  >>> user.getControl(name='contact.add.phones.homePhone.widgets.number')\
  ...     .value = '12 23 23'

  >>> user.getControl('Add Contact').click()

You can now sort the contacts by last and first name now, of course. Clicking
on the "Last Name" table header cell, will leave the order, since the ordering
must be initialized. The second time the order is reversed:

  >>> user.getLink('Last Name').click()
  >>> user.getLink('Last Name').click()

  >>> testing.printElement(user, "//table/tbody/tr/td[1]/a/text()",
  ...                      multiple=True, serialize=False)
  Richter
  Ineichen

Selecting another header will sort on it. Let's choose the first name;
clicking on it once sorts it in ascending order:

  >>> user.getLink('First Name').click()
  >>> testing.printElement(user, "//table/tbody/tr/td[2]/a/text()",
  ...                      multiple=True, serialize=False)
  Roger
  Stephan

Clicking it again, reverses the order:

  >>> user.getLink('First Name').click()
  >>> testing.printElement(user, "//table/tbody/tr/td[2]/a/text()",
  ...                      multiple=True, serialize=False)
  Stephan
  Roger

To delete a contact, you must first select it:

  >>> user.getLink('Roger').click()

At the bototm of the contact form is a delete button that will delete the
entire contact:

  >>> user.getControl('Delete').click()

The user is now gone from the table and we are returned to the add form:

  >>> user.getLink('Roger')
  Traceback (most recent call last):
  ...
  LinkNotFoundError

  >>> user.getControl('Add Contact')
  <SubmitControl name='contact.add.buttons.add' type='submit'>
