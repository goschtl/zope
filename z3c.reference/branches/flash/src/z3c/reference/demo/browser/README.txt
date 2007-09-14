================
 reference demo
================

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

    >>> browser.open('http://localhost/manage')
    >>> browser.url
    'http://localhost/@@contents.html'
    
