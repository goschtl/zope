"""

  >>> import grok
  >>> grok.grok('grok.ftests.admin.apps')

First setup the pluggable authentication system for session based
authentication. This is normaly invoked by an event
handler. Unfortunately the event handler seems not to be called, if
the ftesting setup is set up. We therefore set up the PAU manually.

  >>> root = getRootFolder()
  >>> root is not None
  True

  >>> import grok.admin
  >>> principal_credentials = grok.admin.getPrincipalCredentialsFromZCML()
  >>> principal_credentials
  [{u'login': u'mgr', u'password': u'mgrpw', u'id': u'zope.mgr', u'title': u'Manager'}]

  >>> grok.admin.setupSessionAuthentication(root_folder = root, principal_credentials = principal_credentials)

We should get a login page if trying to get something unauthenticated.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = True
  >>> browser.open("http://localhost/")

  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ... <title>Grok Login</title>
  ...

Now try to log in using *wrong* credentials

  >>> browser.getControl(name='login').value = 'dumbtry'
  >>> browser.getControl('Login').click()
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ... <title>Grok Login</title>
  ...

Okay, we got the login screen again. What about the correct credentials?

  >>> browser.getControl(name='login').value = 'mgr'
  >>> browser.getControl(name='password').value = 'mgrpw'
  >>> browser.getControl('Login').click()
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ... <title>grok administration interface</title>
  ...

Fine. Now we are authorized and can do, whatever we want. To stay
authenticated, we set a header here.
  
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

  
We fetch the standard page, which should provide us a menu to get all
installable grok applications/components.

  >>> browser.open("http://localhost/")
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ...      <legend>Add application</legend>
  ...

We are able to add a mammoth manager...

  >>> browser.getControl('Name your new app:',index=13).value = 'my-mammoth-manager'
  >>> browser.getControl('Create',index=13).click()

  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ... <legend>Installed applications</legend>
  ... <input type="checkbox" class="checkbox" name="items"
             value="my-mammoth-manager" />
      <a href="http://localhost/my-mammoth-manager">
           my-mammoth-manager
           (MammothManager)
        </a>
  ... <legend>Add application</legend>
  ...

Launch the added mammoth manager

  >>> mylink = browser.getLink('my-mammoth-manager (MammothManager)').click()
  >>> print browser.contents
  Let's manage some mammoths!

  >>> print browser.url
  http://localhost/my-mammoth-manager

We are able to delete installed mammoth-managers

  >>> browser.open("http://localhost/")
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ... <legend>Installed applications</legend>
  ...
  >>> ctrl = browser.getControl(name='items')
  >>> ctrl.getControl(value='my-mammoth-manager').selected = True
  >>> browser.getControl('Delete Selected').click()
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ...<legend>Add application</legend>
  ...

"""

import grok

class MammothManager(grok.Application, grok.Container):
    """A mammoth manager"""
    pass

class Index(grok.View):#

    def render(self):
        return u"Let's manage some mammoths!"
