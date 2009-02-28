Create the browser object::

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()

Provide creditial information::

  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> browser.addHeader('Accept-Language', 'en-US')

Open main page::

  >>> browser.open('http://localhost/')
  >>> browser.url
  'http://localhost/'

Open hello page::

  >>> browser.open('http://localhost/@@hello')
  >>> browser.url
  'http://localhost/@@hello'
  >>> 'Hello World' in browser.contents
  True
