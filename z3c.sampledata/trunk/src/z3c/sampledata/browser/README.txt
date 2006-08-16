=============================
Sample Data Generator Manager
=============================

The sample data generator manager allowes the user to configurate the
parameters for the registered generators.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization','Basic mgr:mgrpw')
  >>> browser.handleErrors = False

  >>> browser.open('http://localhost/@@managesamples.html')
  >>> link = browser.getLink(text='samplemanager')
  >>> link.click()
  >>> browser.url
  'http://localhost/@@generatesample.html?manager=samplemanager'

  >>> browser.getControl(name='generator.seed').value = 'lovely'
  >>> browser.getControl(name='lovely.principals.minPrincipals').value = '2'
  >>> browser.getControl(name='lovely.principals.maxPrincipals').value = '34'
  >>> browser.getControl('Generate').click()

