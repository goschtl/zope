=========================================
Basic confirmation and registration views
=========================================

`gocept.registration` comes with a set of basic views and adapters that make it
easy to set up registration-related views for your specific application.

In general you need to provide a registration form where the user can fill in
his data, and a confirmation view which takes the users hash.  In addition you
need to provide configuration for sending out emails (like the from-address, a
template for creating the URL to the confirmation view, and an email
template).

`gocept.registration.demo` demonstrates a simple integration using these
standard components. Mail is being sent to the standard output of your
application.

The registration view is available everywhere with the name `register.html`:

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.open('http://localhost/register.html')
  >>> print browser.contents
  <!DOCTYPE ...
      <title>gocept.registration demo</title>
      ...
      <div class="widget"><input type="text" id="form-widgets-email"
         name="form.widgets.email"
         class="text-widget required textline-field" value="" />
      ...
  >>> browser.getControl('Email address').value = 'john@example.com'
  >>> browser.getControl('Register').click()
  (Ad Ministrator <admin@example.com> -> [u'john@example.com'])
  From: Ad Ministrator <admin@example.com>
  To: john@example.com
  Subject: Please confirm your registration
  <BLANKLINE>
  We received your registration. To activate it, please follow this confirmation
  link:
  <BLANKLINE>
    http://localhost/confirm.html?hash=<SHA-HASH>

The link embedded in the email can be clicked by the user, although we need to
peek into our registration utility, to find the user's actual hash:

  >>> import zope.component
  >>> from gocept.registration.interfaces import IRegistrations
  >>> registrations = zope.component.getUtility(IRegistrations)
  >>> john = registrations.values()[0].hash
  >>> browser.open('http://localhost/confirm.html?hash=%s' % john)
  >>> print browser.contents
  <!DOCTYPE...
  <h1>Success</h1>...
  <p>Your registration was successful.</p>
  ...

A registration can only be confirmed once. If the hash is used a second time,
this will raise an error:

  >>> browser.open('http://localhost/confirm.html?hash=%s' % john)
  >>> print browser.contents
  <!DOCTYPE...
  <h1>Error</h1>...
  <p>Your registration could not be confirmed.</p>
  ...

Probing random hashes will also result in an error:

  >>> browser.open('http://localhost/confirm.html?hash=foo')
  >>> print browser.contents
  <!DOCTYPE...
  <h1>Error</h1>...
  <p>Your registration could not be confirmed.</p>
  ...
