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
""" ZMI unit tests

$Id: testProvideClass.py,v 1.2 2002/06/10 23:29:19 jim Exp $
"""


import unittest, sys, Interface
from Zope.App.OFS.Services.AddableService.tests.AddableSetup import AddableSetup
import Zope.Configuration.name

class MyAddableObject:
    pass

class ProvideClassTest(AddableSetup, unittest.TestCase):

    def testProvideClass(self):
        from Zope.ComponentArchitecture import getService
        from Zope.App.ZMI import provideClass

        provideClass(registry="AddableContent", 
                     qualified_name="My.Test.Addable",
                     _class=MyAddableObject,
                     permission=None,
                     title='Testing')

        obj = getService(None, "Factories").createObject('My.Test.Addable')
        self.assert_(isinstance(obj, MyAddableObject))


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(ProvideClassTest)

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
