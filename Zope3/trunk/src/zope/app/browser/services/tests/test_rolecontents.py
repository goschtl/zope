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

$Id: test_rolecontents.py,v 1.6 2003/08/17 06:05:57 philikon Exp $
"""

import unittest

from zope.interface import Interface, implements
from zope.app.browser.services.role import Contents
from zope.app.services.role import RoleService
from zope.app.browser.container.tests.test_contents \
     import BaseTestContentsBrowserView

class IDummy(Interface):
    pass

class Dummy:
    implements(IDummy)

class Test(BaseTestContentsBrowserView, unittest.TestCase):

    def _TestView__newContext(self):
        from zope.app.content.folder import RootFolder
        from zope.app.context import ContextWrapper
        root = RootFolder()
        container = RoleService()
        return ContextWrapper(container, root, name='sample')

    def _TestView__newView(self, container):
        from zope.publisher.browser import TestRequest
        return Contents(container, TestRequest())

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.main()
