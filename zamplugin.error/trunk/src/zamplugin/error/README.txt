======
README
======

This package contains the Zope Application Management skin. This skin supports 
a modular application management UI without any dependency to the old skin
implementations. The goal of this new skin is to support a more modular
concept which allows us to register only what we need.

Login as manager first:

  >>> from zope.testbrowser.testing import Browser
  >>> manager = Browser()
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')

Check if we can access the page.html view which is registred in the
ftesting.zcml file with our skin:

  >>> manager = Browser()
  >>> manager.handleErrors = False
  >>> manager.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> skinURL = 'http://localhost/++skin++ZAM/index.html'
  >>> manager.open(skinURL)
  >>> manager.url
  'http://localhost/++skin++ZAM/index.html'
