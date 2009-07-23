===========
Wizard Demo
===========

The purpose of the wizard demo is demonstrate the construction of a typical UI
wizard, effectively splitting one form into multiple pages. None of the data
is permanently stored until the wizard is submitted.

To start, we need to open a browser and go to the demo applications overview
screen:

  >>> from z3c.formdemo import testing
  >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
  >>> user = ExtendedTestBrowser()
  >>> user.addHeader('Accept-Language', 'en')
  >>> user.open('http://localhost:8080')

Since all demos are purely public, there is no need to log in. Let's now click
on the "Wizard" link:

  >>> user.getLink('Wizard').click()

You are now seeing the first step of the wizard, which asks for personal
information:

  >>> testing.printElement(user, "//h1")
  <h1>Wizard Demo - Person Demographics</h1>

  >>> testing.printElement(user, "//legend")
  <legend>Personal Information</legend>

Let's fill out the form and save the data:

  >>> user.getControl('First Name').value = 'Stephan'
  >>> user.getControl('Last Name').value = 'Richter'

  >>> user.getControl('Phone').value = '+1 555 276-3761'
  >>> user.getControl('Email').value = 'stephan.richter_(at)_gmail.com'

  >>> user.getControl('Save').click()

Rhe "Save" button causes the form to be submitted, but not to proceed to the
next step. A message that the data has been successfully saved in shown:

  >>> testing.printElement(user, "//div[@class='summary']")
  <div class="summary">Data successfully updated.</div>

Pressing the "Clear" button (which only appears on the first step) will clear
out the data of all steps:

  >>> user.getControl('Clear').click()

  >>> user.getControl('First Name').value
  ''
  >>> user.getControl('Last Name').value
  ''
  >>> user.getControl('Phone').value
  ''
  >>> user.getControl('Email').value
  ''

So let's now fill out the form and click the next button this time.

  >>> user.getControl('First Name').value = 'Stephan'

  >>> user.getControl('Phone').value = '+1 555 276-3761'
  >>> user.getControl('Email').value = 'stephan.richter_(at)_gmail.com'

  >>> user.getControl('Next').click()

But we forgot the last name, which means the form does nto successfully submit
and an error message is shown. So we are still at step 1:

  >>> testing.printElement(user, "//legend")
  <legend>Personal Information</legend>

Filling in the missing required field will allow the action to be successful:

  >>> user.getControl('Last Name').value = 'Richter'
  >>> user.getControl('Next').click()

You are now forwarded to the second step:

  >>> testing.printElement(user, "//legend")
  <legend>Address</legend>

The "Next" button does not only forward the user to the second step, but also
stores the data. Clicking on "Previous" will bring us back to the first
screen. But let's first fill out step 2, since the "Previous" button also
stores the data of the current step:

  >>> user.getControl('Street').value = '110 Main Street'
  >>> user.getControl('Zip').value = '01754'

  >>> user.getControl('Previous').click()

But forgetting a required field does not get you to the previous step.

  >>> testing.printElement(user, "//legend")
  <legend>Address</legend>

Filling out all information causes the action to be successful:

  >>> user.getControl('City').value = 'Maynard'
  >>> user.getControl('Previous').click()

So back at step 1, we can see that all the personal information is there.

  >>> user.getControl('First Name').value
  'Stephan'
  >>> user.getControl('Last Name').value
  'Richter'
  >>> user.getControl('Phone').value
  '+1 555 276-3761'
  >>> user.getControl('Email').value
  'stephan.richter_(at)_gmail.com'

You can also navigate through the wizard by clicking on the step number on the
top, so let's go to step 2 by clicking on that link:

  >>> user.getLink('2').click()
  >>> testing.printElement(user, "//legend")
  <legend>Address</legend>

Note that no data is saved, when using this link. We also notice that all the
data fields are filled out:

  >>> user.getControl('Street').value
  '110 Main Street'
  >>> user.getControl('Zip').value
  '01754'
  >>> user.getControl('City').value
  'Maynard'

Let's now go to the third and forth step, filling them out.

  >>> user.getControl('Next').click()

  >>> user.getControl('First Name').value = 'Wolfgang'
  >>> user.getControl('Last Name').value = 'Richter'
  >>> user.getControl('Phone').value = '+49 33 1271568'
  >>> user.getControl('Email').value = 'wrichter@telekom.de'
  >>> user.getControl('Street').value = u'Dorfstraße 12'.encode('utf-8')
  >>> user.getControl('Zip').value = '01945'
  >>> user.getControl('City').value = 'Tetta'

  >>> user.getControl('Next').click()

  >>> user.getControl('First Name').value = 'Marion'
  >>> user.getControl('Last Name').value = 'Richter'
  >>> user.getControl('Phone').value = '+49 33 1271568'
  >>> user.getControl('Street').value = u'Dorfstraße 12'.encode('utf-8')
  >>> user.getControl('Zip').value = '01945'
  >>> user.getControl('City').value = 'Tettau'

  >>> user.getControl('Next').click()

We are now at the final screen. As you will notice, initially there is no
button that allows submitting the wizard:

  >>> user.getControl('Finish')
  Traceback (most recent call last):
  ...
  LookupError: label 'Finish'

This is because not all required fields have been filled out. Filling out the
last step and saving it, ...

  >>> user.getControl('Name').value = 'Myself'
  >>> user.getControl('Street').value = '110 Main Street'
  >>> user.getControl('Zip').value = '01754'
  >>> user.getControl('City').value = 'Maynard'

  >>> user.getControl('Save').click()

... will allow the "Finish" button to show:

  >>> user.getControl('Finish')
  <SubmitControl name='form.buttons.finish' type='submit'>

Clicking it, brings us to the final summary screen:

  >>> user.getControl('Finish').click()
  >>> user.url
  'http://localhost:8080/summary.html'
