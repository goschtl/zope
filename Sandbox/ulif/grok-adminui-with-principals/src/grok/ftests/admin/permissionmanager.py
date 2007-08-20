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

Let's start by logging in:

  >>> import grok
  >>> grok.grok('grok.ftests.admin.permissionmanager')
  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

Then we have a look at the permissions screen.

  >>> browser.open("http://localhost/permissions")
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ...  <h1>Edit Roles and Permissions</h1>
  ...

Here we can assign permissions to the roles given on the site. If we
do nothing and save all values, we get informed, that the permissions
were updated:

  >>> save_button = browser.getControl('Save')
  >>> save_button.type
  'submit'

  >>> save_button.click()
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ... <span class="emph">Permissions successfully updated.</span>
  ...

We pick an arbitrary permission/role combination and look whether we
can set it. One permission not needed below is
``zope.app.dublincore.change``.

  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ... <td>zope.app.dublincore.change</td>
  ...

It can be set for the only user available here, the Manager
account. The appropriate select box should have a name like
`prolezope.app.dublincore.changezope.Manager` which is a combination
of the permission id, the role id and a marker at the beginning. Is a
selectbox if that name available?

  >>> selectbox = browser.getControl(name='prolezope.app.dublincore.changezope.Manager')
  >>> selectbox
  <ListControl name='prolezope.app.dublincore.changezope.Manager' type='select'>

Fine. What values to select from are offered?

  >>> selectbox.displayOptions
  ['Unset', 'Allow', 'Deny']

These settings should be available for all permission/role
combinations. The currently displayed value should be 'Unset' (which
should be true for all values as well):

  >>> selectbox.displayValue
  ['Unset']

We select another value. Let's set the `zope.app.dublincore.change`
permission for the user `zope.Manager` to 'Allow':

  >>> selectbox.getControl(value='Allow').selected = True
  >>> selectbox.displayValue
  ['Allow']

and save that setting, submitting the form:

  >>> browser.getControl('Save').click()

Now let's see, whether everything went fine.

  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ... <span class="emph">Permissions successfully updated.</span>
  ...

  >>> selectbox = browser.getControl(name='prolezope.app.dublincore.changezope.Manager')
  >>> selectbox.displayValue
  ['Allow']


"""

