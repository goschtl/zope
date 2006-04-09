======
README
======

Browser tests
-------------

Setup testbrowser for IWebSiteBrowserSkin functional tests.

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
    >>> browser.handleErrors = False


Check if the IWebSiteBrowserSkin skin is a vailable.

    >>> browser.open('http://localhost/++skin++ZSCP/@@contents.html')
    >>> browser.url
    'http://localhost/++skin++ZSCP/@@contents.html'
