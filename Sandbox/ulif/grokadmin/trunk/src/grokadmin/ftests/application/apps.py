##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""

===============================================
Add and remove applications using ``GrokAdmin``
===============================================

Setup a testing environment::

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
  >>> root = getRootFolder()

Now we install an instance of ``GrokAdmin`` named `admin`::

  >>> from grokadmin.app import GrokAdmin
  >>> root['admin'] = GrokAdmin()
  >>> list(root.keys())
  [u'admin']
  
We fetch the standard page, which should provide us a menu to get all
installable grok applications/components::

  >>> browser.open("http://localhost/admin")
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ...      <legend>Add application</legend>
  ...

The opening screen should inform us, that there is our GrokAdmin
installed::

  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ...<legend>Installed applications</legend>
  ...
  ...<a href="http://localhost/admin">
  ...

We are able to add a mammoth manager...

  >>> subform = browser.getForm(name='MammothManager')
  >>> subform.getControl('Name your new app:').value = 'my-mammoth-manager'
  >>> subform.getControl('Create').click()

  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ...<legend>Installed applications</legend>
  ...
  ...<a href="http://localhost/my-mammoth-manager">
  ...

Launch the added mammoth manager

  >>> mylink = browser.getLink('my-mammoth-manager (MammothManager)').click()
  >>> print browser.contents
  Let's manage some mammoths!

  >>> print browser.url
  http://localhost/my-mammoth-manager

"""
"""

We can go to the object browser for every installed application:

  >>> browser.open("http://localhost/applications")
  >>> browser.getLink('object browser').click()
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ...<span ...>...<a href=...>MammothManager</a> object at ...></span>
  ... 

We are able to delete installed mammoth-managers

  >>> browser.open("http://localhost/applications")
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ... <legend>Installed applications</legend>
  ...
  >>> ctrl = browser.getControl(name='items')
  >>> ctrl.getControl(value='my-mammoth-manager').selected = True
  >>> browser.getControl('Delete Selected').click()
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ... <p ...>Currently no working applications...are installed.</p>
  ...
  ...<legend>Add application</legend>
  ...

"""

import grok

class MammothManager(grok.Application, grok.Container):
    """A mammoth manager"""
    pass

class Index(grok.View):#

    def render(self):
        return u"Let's manage some mammoths!"
