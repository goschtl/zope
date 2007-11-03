====================
Datetime Widget Demo
====================

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
    >>> browser.getControl('Several dates').value = '2006-11-20 2006-11-21 2006-11-22'
    >>> browser.getControl('Change').click()

And they will be saved:

    >>> 'Required input is missing' in browser.contents
    False

    >>> '2006-11-15' in browser.contents
    True
    >>> '2006-11-16' in browser.contents
    True
    >>> '07:49' in browser.contents
    True
    >>> '19:46' in browser.contents
    True
    >>> '2006-11-20 2006-11-21 2006-11-22' in browser.contents
    True

If we do not fill some fields, we get missing value errors

    >>> browser.getControl('Start Date').value = ''
    >>> browser.getControl('Change').click()
    >>> 'Required input is missing' in browser.contents
    True

Let's step back:

    >>> browser.getControl('Start Date').value = '2006-11-15'
    >>> browser.getControl('Change').click()
    >>> 'Required input is missing' in browser.contents
    False

Now let's try not filling a date set field:

    >>> browser.getControl('Several dates').value = ''
    >>> browser.getControl('Change').click()
    >>> 'Required input is missing' in browser.contents
    True

