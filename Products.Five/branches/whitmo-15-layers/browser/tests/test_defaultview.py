##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Test Default View functionality

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

def test_default_view():
    """
    Test default view functionality

    Let's register a couple of default views and make our stub classes
    default viewable:

      >>> import Products.Five.browser.tests
      >>> from Products.Five import zcml
      >>> zcml.load_config("configure.zcml", Products.Five)
      >>> zcml.load_config('defaultview.zcml', Products.Five.browser.tests)

    Now let's add a couple of stub objects:

      >>> from Products.Five.tests.testing.simplecontent import manage_addSimpleContent
      >>> from Products.Five.tests.testing.simplecontent import manage_addCallableSimpleContent
      >>> from Products.Five.tests.testing.simplecontent import manage_addIndexSimpleContent

      >>> manage_addSimpleContent(self.folder, 'testoid', 'Testoid')
      >>> manage_addCallableSimpleContent(self.folder, 'testcall', 'TestCall')
      >>> manage_addIndexSimpleContent(self.folder, 'testindex', 'TestIndex')

    As a last act of preparation, we create a manager login:

      >>> uf = self.folder.acl_users
      >>> uf._doAddUser('manager', 'r00t', ['Manager'], [])

    BBB This is a test of backwards comaptibility with Five 1.3/Zope
    2.9.  The deprecated directive five:defaultViewable would before
    make index.html the default view. Test that this is still the
    case.  five:defaultViewable goes away in Zope 2.12, and this test
    goes then too:

      >>> import warnings
      >>> showwarning = warnings.showwarning
      >>> warnings.showwarning = lambda *a, **k: None

      >>> zcml.load_string('''
      ... <configure xmlns:five="http://namespaces.zope.org/five">
      ...   <five:defaultViewable
      ...     class="Products.Five.tests.testing.simplecontent.SimpleContent" />
      ... </configure>''')    
      >>> print http(r'''
      ... GET /test_folder_1_/testoid HTTP/1.1
      ... Authorization: Basic manager:r00t
      ... ''')
      HTTP/1.1 200 OK
      ...
      The eagle has landed

      >>> warnings.showwarning = showwarning

    But if we want to, we can specify another default view with
    browser:defaultView:

      >>> zcml.load_string('''
      ... <configure xmlns:browser="http://namespaces.zope.org/browser">
      ...   <browser:defaultView
      ...     for="Products.Five.tests.testing.simplecontent.ISimpleContent"
      ...     name="eagledefaultview.txt" />
      ... </configure>''')
      >>> print http(r'''
      ... GET /test_folder_1_/testoid HTTP/1.1
      ... Authorization: Basic manager:r00t
      ... ''')
      HTTP/1.1 200 OK
      ...
      The mouse has been eaten by the eagle

    In Five 1.5 ``index_html`` you can no longer set default views to anything
    else than views:
    
      >>> print http(r'''
      ... GET /test_folder_1_/testindex HTTP/1.1
      ... ''')
      HTTP/1.1 404 Not Found
      ...

    Disabled __call__ overriding for now.  Causes more trouble than it
    fixes.  Thus, no test here:

      #>>> print http(r'''
      #... GET /test_folder_1_/testcall HTTP/1.1
      #... ''')
      #HTTP/1.1 200 OK
      #...
      #Default __call__ called


    Clean up:

      >>> from zope.app.testing.placelesssetup import tearDown
      >>> tearDown()
    """

def test_suite():
    from Testing.ZopeTestCase import FunctionalDocTestSuite
    return FunctionalDocTestSuite()

if __name__ == '__main__':
    framework()
