======
README
======

This package provides the server control management. The zam.skin is used as 
basic skin for this test.

Login as manager first:

  >>> from zope.testbrowser.testing import Browser
  >>> manager = Browser()
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')

Check if we can access the page.html view which is registred in the
ftesting.zcml file for the ``ZAM`` skin:

  >>> manager = Browser()
  >>> manager.handleErrors = False
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> skinURL = 'http://localhost/++skin++ZAM/index.html'
  >>> manager.open(skinURL)
  >>> manager.url
  'http://localhost/++skin++ZAM/index.html'
