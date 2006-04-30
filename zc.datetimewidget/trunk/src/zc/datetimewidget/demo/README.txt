======================
 Datetime Widget Demo
======================

This demo packe provides a simple content class which uses the
zc.datetimewidget

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
    >>> browser.open('http://localhost/@@contents.html')

It can be added by clicking on the "Datetimewidget Demo" link in the
add menu. And giving it a name.

    >>> link = browser.getLink('Datetimewidget Demo')
    >>> link.click()
    >>> nameCtrl = browser.getControl(name='new_value')
    >>> nameCtrl.value = 'mydemo'
    >>> applyCtrl = browser.getControl('Apply')
    >>> applyCtrl.click()
    >>> link = browser.getLink('mydemo')
    >>> link.click()
    >>> browser.url
    'http://localhost/mydemo/@@edit.html'


