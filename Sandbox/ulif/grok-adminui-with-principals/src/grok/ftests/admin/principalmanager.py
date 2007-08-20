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
  >>> grok.grok('grok.ftests.admin.principalmanager')
  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')

Then we have a look at the permissions screen.

  >>> browser.open("http://localhost/users")
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ...  <h1>Edit Principals</h1>
  ...

The principalmanager needs a working pluggable authentication utility
(PAU) to do its job. However, in the default ftesting setup there is
no PAU available, but only the default basic auth authentication
mechanism. Our principalmanager should check this and give an
appropriate message:

  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ...This usermanagement screen is disabled because no working...
  ...pluggable authentication utility (PAU) with a pluggable...
  ...authenticator could be found. Please register one in the...
  ...site manager of your Zope root to enable this screen again...
  ...

So we have to set up our own PAU first:

  >>> root = getRootFolder()
  >>> import grok.admin
  >>> principal_credentials = grok.admin.getPrincipalCredentialsFromZCML()
  >>> principal_credentials
  [{u'login': u'mgr', u'password': u'mgrpw', u'id': u'zope.mgr', u'title': u'Manager'}]

  >>> grok.admin.setupSessionAuthentication(root_folder = root, principal_credentials = principal_credentials)

We should get a login page if trying to get something unauthenticated.

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = True
  >>> browser.open("http://localhost/")

  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ... <title>Grok Login</title>
  ...

We log in with the fsetup credentials:

  >>> browser.getControl(name='login').value = 'mgr'
  >>> browser.getControl(name='password').value = 'mgrpw'
  >>> browser.getControl('Login').click()
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ... <title>grok administration interface</title>
  ...

and got to the principal manager clicking 'Server Control' and
afterwards 'Principals and Roles':

  >>> browser.getLink('Server Control').click()
  >>> browser.getLink('Principals and Roles').click()

Now (as we did setup a working PAU), we should have a possibility to add
new principals:

  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ... <legend>Add new principal:</legend>
  ...

Cool. Let's try it. We have to give a login, a title, a description
and a password. Because there should be several fields with that names
in the page we only consider the first form in the page, which should
be the `add principal` form:

  >>> addform = browser.getForm(index=0)

We fill in this subform with the values of Manfred the
Mammoth. Because Manfred is not too smart, we choose a plain password
for him.

  >>> addform.getControl(name='login').value = 'manfred'
  >>> addform.getControl(name='title').value = 'Manfred the Mammoth'
  >>> addform.getControl(name='description').value = 'A good friend of Grok.'
  >>> addform.getControl(name='passwd').value = 'm'

No we are ready to add Manfred as principal:

  >>> browser.getControl('add principal').click()
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ...
  ... Existing Principals:
  ...
  ... <legend>Manfred the Mammoth</legend>
  ...

We got a new principal. However, Manfred got no permissions, because
he got no role assigned. To check this, we first have to find out,
which subform represents Manfred:

  >>> manfred_form = browser.getForm(index=1)
  >>> try:
  ...   delete_button = manfred_form.getControl('Delete this user')
  ... except LookupError:
  ...   manfred_form = browser.getForm(index=2)
  ...   delete_button = manfred_form.getControl('Delete this user')

Now we check the roles assigned to Manfred:

  >>> roles = manfred_form.getControl(name='roles')
  >>> roles
  <ListControl name='roles' type='select'>

  >>> roles.multiple
  True

  >>> roles.value
  []
  
No roles for Manfred. What roles are available?

  >>> roles.options
  ['zope.Manager']

Ooh, that's little. Anyway, we try to give Manfred manager privileges:

  >>> roles.value =   ['zope.Manager']

and change its values:

  >>> manfred_form.getControl(name='title').value = 'Manfred the friendly Mammoth'
  >>> manfred_form.getControl(name='description').value = 'A good and very tall friend'
  >>> manfred_form.getControl(name='passwd').value = 'M'
  >>> manfred_form.getControl('update').click()
  
Were the changes committed?

  >>> manfred_form = browser.getForm(index=1)
  >>> try:
  ...   delete_button = manfred_form.getControl('Delete this user')
  ... except LookupError:
  ...   manfred_form = browser.getForm(index=2)
  ...   delete_button = manfred_form.getControl('Delete this user')
  >>> manfred_form.getControl(name='title').value
  'Manfred the friendly Mammoth'

  >>> manfred_form.getControl(name='description').value
  'A good and very tall friend'

  >>> manfred_form.getControl(name='roles').value
  ['zope.Manager']

This looks good. To really check, whether the changes are effective,
we now logout and try to enter the admin-UI as Manfred:

  >>> browser.getLink('log out').click()
  >>> print browser.contents
  <html>
  ...
  ... You have been logged out.
  ...
  
  >>> browser.open("http://localhost/")
  >>> browser.getControl(name='login').value = 'manfred'
  >>> browser.getControl(name='password').value = 'M'
  >>> browser.getControl('Login').click()
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ... <title>grok administration interface</title>
  ...

We logged in successfully as Manfred. Now logout and login again, but
as the Manager user, to do the last tests.

  >>> browser.getLink('log out').click()
  >>> browser.open("http://localhost/")
  >>> browser.getControl(name='login').value = 'mgr'
  >>> browser.getControl(name='password').value = 'mgrpw'
  >>> browser.getControl('Login').click()
  >>> browser.getLink('Server Control').click()
  >>> browser.getLink('Principals and Roles').click()
  >>> manfred_form = browser.getForm(index=1)
  >>> try:
  ...   delete_button = manfred_form.getControl('Delete this user')
  ... except LookupError:
  ...   manfred_form = browser.getForm(index=2)
  ...   delete_button = manfred_form.getControl('Delete this user')

Now we try to delete Manfred:

  >>> 'manfred' in browser.contents
  True
  
  >>> delete_button.click()
  >>> 'manfred' in browser.contents
  False

If we now try to login as Manfred:

  >>> browser.getLink('log out').click()
  >>> browser.open("http://localhost/")
  >>> browser.getControl(name='login').value = 'manfred'
  >>> browser.getControl(name='password').value = 'M'
  >>> browser.getControl('Login').click()
  >>> print browser.contents
  <html xmlns="http://www.w3.org/1999/xhtml">
  ... <title>Grok Login</title>
  ...

We are still logged out.

"""
