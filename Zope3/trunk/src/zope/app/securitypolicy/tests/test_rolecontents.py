##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: test_rolecontents.py,v 1.1 2004/02/27 12:46:33 philikon Exp $
"""

import unittest

from zope.interface import Interface, implements
from zope.app.browser.container.tests.test_contents \
     import BaseTestContentsBrowserView, Principal
from zope.app.folder import rootFolder
from zope.app.container.contained import contained

from zope.app.securitypolicy.browser import Contents
from zope.app.securitypolicy.role import RoleService

class IDummy(Interface):
    pass

class Dummy:
    implements(IDummy)

class Test(BaseTestContentsBrowserView, unittest.TestCase):

    def _TestView__newContext(self):
        root = rootFolder()
        container = RoleService()
        return contained(container, root, name='sample')

    def _TestView__newView(self, container):
        from zope.publisher.browser import TestRequest
        request = TestRequest()
        request.setUser(Principal())
        return Contents(container, request)

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.main()
