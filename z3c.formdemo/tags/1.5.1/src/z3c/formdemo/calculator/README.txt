===============
Calculator Demo
===============

The purpose of the calculator demo is demonstrate the concept of buttons and
their actions and how the framework allows high degrees of customization.

To start, we need to open a browser and go to the demo applications overview
screen:

  >>> from z3c.formdemo import testing
  >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
  >>> user = ExtendedTestBrowser()
  >>> user.addHeader('Accept-Language', 'en')
  >>> user.open('http://localhost:8080')

Since all demos are purely public, there is no need to log in. Let's now click
on the "Calculator" link:

  >>> user.getLink('Calculator').click()

You are now seeing the calculator:

  >>> testing.printElement(user, "//h1")
  <h1>
    <span class="name">A simple calculator</span>
    <span class="version">v1.0</span>
  </h1>

Let's start by doing a simple addition (``35 + 4.3 = ``:

  >>> user.getControl('3').click()
  >>> user.getControl('5').click()

  >>> user.getControl('+').click()

  >>> user.getControl('4').click()
  >>> user.getControl('.').click()
  >>> user.getControl('3').click()

  >>> user.getControl('=').click()

The result is shown within the display structure:

  >>> testing.printElement(
  ...     user, "//div[@id='current']/span[@class='value']/text()",
  ...     serialize=False)
  39.3

When an illegal operation occurs, an error message is shown:

  >>> user.getControl('/').click()
  >>> user.getControl('0').click()
  >>> user.getControl('=').click()

  >>> testing.printElement(
  ...     user, "//div[@id='current']/span[@class='value']/text()",
  ...     serialize=False)
  -E-

The entire calculator state can be reset at any time using the clear button:

  >>> user.getControl('C').click()

  >>> testing.printElement(
  ...     user, "//div[@id='current']/span[@class='value']/text()",
  ...     serialize=False)
  0

If a non-valid number is entered, it is just replaced by zero:

  >>> user.getControl('4').click()
  >>> user.getControl('.').click()
  >>> user.getControl('.').click()
  >>> user.getControl('3').click()

  >>> user.getControl('=').click()

  >>> testing.printElement(
  ...     user, "//div[@id='current']/span[@class='value']/text()",
  ...     serialize=False)
  0
