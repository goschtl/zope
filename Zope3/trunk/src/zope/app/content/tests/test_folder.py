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
from unittest import TestCase
from zope.app.component.tests.test_servicemanagercontainer \
     import BaseTestServiceManagerContainer
from zope.app.container.tests.test_icontainer import BaseTestIContainer

class Test(BaseTestIContainer, BaseTestServiceManagerContainer, TestCase):

    def makeTestObject(self):
        from zope.app.content.folder import Folder
        return Folder()

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )
