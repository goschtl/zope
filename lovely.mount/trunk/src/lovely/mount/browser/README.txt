=========================
Mount Point Browser Views
=========================

We provide default views which are relevant for administering mount points.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization','Basic mgr:mgrpw')
  >>> browser.handleErrors = False

  >>> browser.open('http://localhost/@@contents.html')
  >>> browser.getLink('Mountpoint Container').click()
  >>> browser.url
  'http://localhost/+/addMountpointContainer.html='
  >>> browser.getControl(name="form.__name__").value=u'mp'
  >>> browser.getControl("Database Name").value=['2']

  >>> browser.getControl('Add').click()
  >>> browser.open('http://localhost/mp/@@contents.html')
  >>> browser.getLink('Folder').click()
  >>> browser.getControl(name='new_value').value=u"Folder in MP"
  >>> browser.getControl('Apply').click()
  >>> print browser.url
  http://localhost/mp/@@contents.html

  >>> browser.getLink('Folder in MP').click()