============================
SQL Hello World Message Demo
============================

The purpose of the SQL Hello World Message demo is to demonstrate how
non-bject data can be manipulated and displayed using the form framework.

To start, we need to open a browser and go to the demo applications overview
screen:

  >>> from z3c.formdemo import testing
  >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
  >>> user = ExtendedTestBrowser()
  >>> user.addHeader('Accept-Language', 'en')
  >>> user.open('http://localhost:8080')

Since all demos are purely public, there is no need to log in. Let's now click
on the "SQL Hello World" link:

  >>> user.getLink('SQL Hello World').click()

The initial page of the demo is the list of all messages. This screen exists,
because the ZMI management screens are not helpful for unmapped relational data.

  >>> testing.printElement(user, "//h1")
  <h1>SQL Hello World Message Demo</h1>

Let's make sure the database is truly empty:

  >>> testing.printElement(user, "//table/tbody", multiple=True)

We can now initialize the database using one of the action links below the
table:

  >>> user.getLink('[Initialize the database]').click()
  >>> testing.printElement(user, "//div[@class='summary']", multiple=True)

The page returns with no notable messages. Clicking the link again results in
an error, because the database is already initialized:

  >>> user.getLink('[Initialize the database]').click()
  >>> testing.printElement(user, "//div[@class='summary']")
  <div class="summary">Database Message: cannot create MSG, exists</div>

Let's now add a new message:

  >>> user.getLink('[Add message]').click()

You are now represented with the message add form.

  >>> user.url
  'http://localhost:8080/addSQLHelloWorld.html'

If we submit the form by clicking on add, ...

  >>> user.getControl('Add').click()

... the same page returns telling us we have some errors:

  >>> testing.printElement(user, "//div[@class='summary']")
  <div class="summary">There were some errors.</div>

This is because we forgot to enter the "Who" field, which is required:

  >>> testing.printElement(user, "//ul[@class='errors']/li")
  <li>
     Who: <div class="error">Required input is missing.</div>
  </li>

Let's now fill out all the required fields and try to add the message again:

  >>> user.getControl('Who').value = u'Stephan'
  >>> user.getControl('When').value = u'7/1/07'
  >>> user.getControl('Add').click()

Once submitted, the message is now added to the database and we are returned
back to the overview:

  >>> testing.printElement(user, "//table/tbody/tr[1]")
  <tr class="odd"><td class="sorted-on">
      <a href="showSQLHelloWorld.html?id=0">0</a>
    </td>
    <td class="">
      <a href="showSQLHelloWorld.html?id=0">Stephan</a>
    </td>
    <td class="">
      <a href="showSQLHelloWorld.html?id=0">2007-07-01</a>
    </td>
    <td class="">
      <a href="showSQLHelloWorld.html?id=0">cool</a>
    </td>
    <td class="">
      <a href="showAllSQLHelloWorld.html?delete=0">[Delete]</a>
    </td>
  </tr>

Clicking on any data item, brings us to the message display screen:

  >>> user.getLink('Stephan').click()
  >>> testing.printElement(user, "//h1")
  <h1>
    A
    <span id="form-widgets-what"
          class="select-widget required choice-field"><span
      class="selected-option">cool</span></span>
    Hello World
    from
    <span id="form-widgets-who"
          class="text-widget required textline-field">Stephan</span>
    on
    <span id="form-widgets-when"
          class="text-widget required date-field">7/1/07</span>
    !
  </h1>

The message's edit form can be accessed by clicking on the "Edit Message"
link:

  >>> user.getLink('Edit Message').click()

When immediately pressing "Apply", a message appears telling us that no data
has been changed:

  >>> user.getControl('Apply', index=0).click()
  >>> testing.printElement(user, "//div[@class='summary']")
  <div class="summary">No changes were applied.</div>

Let's now change the name and submit the form:

  >>> user.getControl('Who').value = u'Roger'
  >>> user.getControl('Apply', index=0).click()

The page now informs us that the data has been updated:

  >>> testing.printElement(user, "//div[@class='summary']")
  <div class="summary">Data successfully updated.</div>

When pressing the "Apply and View" button, the changed data is stored and the
user is also forwarded to the view page again:

  >>> user.getControl('What').getControl('best').click()
  >>> user.getControl('Apply and View').click()

Of course, the view shows the latest data:

  >>> testing.printElement(user, "//h1")
  <h1>
    A
    <span id="form-widgets-what"
          class="select-widget required choice-field"><span
      class="selected-option">best</span></span>
    Hello World
    from
    <span id="form-widgets-who"
          class="text-widget required textline-field">Roger</span>
    on
    <span id="form-widgets-when"
          class="text-widget required date-field">7/1/07</span>
    !
  </h1>

From the display screen you can also return to the overview:

  >>> user.getLink('[Show All Messages]').click()
  >>> user.url
  'http://localhost:8080/showAllSQLHelloWorld.html'

Let's now add a new message:

  >>> user.getLink('[Add message]').click()

  >>> user.getControl('Who').value = u'Stephan'
  >>> user.getControl('When').value = u'7/2/07'
  >>> user.getControl('Add').click()

As you probably already guessed, the table headers can be used to sort
items. Clicking on the "Id" table header cell, will leave the order,
since the ordering must be initialized. The second time the order is reversed:

  >>> user.getLink('Id').click()
  >>> user.getLink('Id').click()

  >>> testing.printElement(user, "//table/tbody/tr/td[1]/a/text()",
  ...                      multiple=True, serialize=False)
  1
  0

Selecting another header will sort on it. Let's choose the "Who" column;
clicking on it once sorts it in ascending order:

  >>> user.getLink('Who').click()
  >>> testing.printElement(user, "//table/tbody/tr/td[2]/a/text()",
  ...                      multiple=True, serialize=False)
  Roger
  Stephan

Clicking it again, reverses the order:

  >>> user.getLink('Who').click()
  >>> testing.printElement(user, "//table/tbody/tr/td[2]/a/text()",
  ...                      multiple=True, serialize=False)
  Stephan
  Roger

To delete a contact, you Simply click on the "Delete" link of the
corresponding row:

  >>> user.getLink('[Delete]', index=1).click()

The message is now gone from the table:

  >>> user.getLink('Roger')
  Traceback (most recent call last):
  ...
  LinkNotFoundError
