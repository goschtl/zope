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

$Id: test_rolecontents.py,v 1.2 2004/01/14 22:55:35 chrism Exp $
"""

import unittest

from zope.interface import Interface, implements
from zope.products.securitypolicy.browser import Contents
from zope.products.securitypolicy.role import RoleService
from zope.app.browser.container.tests.test_contents \
     import BaseTestContentsBrowserView, Principal
from zope.app.content.folder import rootFolder
from zope.app.container.contained import contained

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
