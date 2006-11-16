======================
 Datetime Widget Demo
======================

This demo packe provides a simple content class which uses the
zc.datetimewidget

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.handleErrors = False
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

We can fill in the values

    >>> browser.getControl('Start Date').value = '2006-11-15'
    >>> browser.getControl('End Date').value = '2006-11-16'
    >>> browser.getControl('Start Datetime').value = '2006-11-15T07:49:31Z'
    >>> browser.getControl('End Datetime').value = '2006-11-16T19:46:00Z'
    >>> browser.getControl('Change').click()

If we do not fill them in, we get missing value errors

    >>> browser.getControl('Start Date').value = ''
    >>> browser.getControl('Start Datetime').value = ''
    >>> browser.getControl('More dates').value = ''
    >>> browser.getControl('Change').click()
    >>> 'Required input is missing' in browser.contents
    True

