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
from Zope.App.ComponentArchitecture.tests.testServiceManagerContainer \
     import BaseTestServiceManagerContainer
from Zope.App.OFS.Container.tests.testIContainer import BaseTestIContainer

class Test(BaseTestIContainer, BaseTestServiceManagerContainer, TestCase):

    def _Test__new(self):
        from Zope.App.OFS.Content.Folder.Folder import Folder
        return Folder()

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )
