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

$Id: testContents.py,v 1.3 2002/06/13 23:15:42 jim Exp $
"""

import unittest

from Interface import Interface
from Zope.App.OFS.Services.RoleService.Views.Browser.Contents import Contents
from Zope.App.OFS.Services.RoleService.RoleService import RoleService
from Zope.App.OFS.Container.Views.Browser.tests.testContents \
     import BaseTestContentsBrowserView

class IDummy(Interface):
    pass

class Dummy:
    __implements__ = IDummy
    
class Test(BaseTestContentsBrowserView, unittest.TestCase):

    def _TestView__newContext(self):
        return RoleService()

    def _TestView__newView(self, container):
        from Zope.Publisher.Browser.BrowserRequest import TestRequest
        return Contents(container, TestRequest())

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )

if __name__=='__main__':
    unittest.main()
