========================
Hello World Message Demo
========================

The "Hello World Message" demo is intended to demonstrate the most minimal
setup required to get add, edit and display to work.

To start, we need to open a browser and go to the demo applications overview
screen:

  >>> from z3c.formdemo import testing
  >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
  >>> user = ExtendedTestBrowser()
  >>> user.addHeader('Accept-Language', 'en')
  >>> user.open('http://localhost:8080')

Since all demos are purely public, there is no need to log in. Let's now click
on the "Hello World" link:

  >>> user.getLink('Hello World').click()

You are now represented with the message add form.

  >>> user.url
  'http://localhost:8080/addHelloWorld.html'

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

Once submitted, the message is now added to the database and the display view
is shown:

  >>> testing.printElement(user, "//h1")
  <h1>
    A <span id="form-widgets-what"
            class="select-widget required choice-field"><span
            class="selected-option">cool</span></span>
   Hello World
    from <span id="form-widgets-who"
               class="text-widget required textline-field">Stephan</span>
  <BLANKLINE>
    on <span id="form-widgets-when"
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
    A <span id="form-widgets-what"
            class="select-widget required choice-field"><span
      class="selected-option">best</span></span>
   Hello World
    from <span id="form-widgets-who"
               class="text-widget required textline-field">Roger</span>
  <BLANKLINE>
    on <span id="form-widgets-when"
             class="text-widget required date-field">7/1/07</span>
  !
  </h1>
