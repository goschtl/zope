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
import unittest

from Zope.App.OFS.Content.Folder.Views.Browser.FolderContents import FolderContents
from Zope.App.OFS.Content.Folder.Folder import Folder
from Zope.App.OFS.Container.Views.Browser.tests.testContents \
     import BaseTestContentsBrowserView

class Test(BaseTestContentsBrowserView, unittest.TestCase):

    def _TestView__newContext(self):
        return Folder()

    def _TestView__newView(self, container):
        from Zope.Publisher.Browser.BrowserRequest import TestRequest
        return FolderContents(container, TestRequest())

    def testAddServiceManager(self):
        folder = Folder()
        fc = FolderContents(folder, None)
        fc.addServiceManager()
        self.failUnless(folder.hasServiceManager())
        self.assertRaises('HasServiceManager', fc.addServiceManager)

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )

if __name__=='__main__':
    unittest.main()
