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
from zope.app.utilities.tests.unitfixtures import *  # hehehe
from zope.interface.interface import Attribute
from zope.interface.tests.test_interface import InterfaceTests as BaseTest
from zope.app.tests import setup

class InterfaceTests(BaseTest):

    def setUp(self):
        setup.placefulSetUp()

    def tearDown(self):
        setup.placefulTearDown()

class _I1(Schema):

    def f11(): pass
    def f12(): pass
    f12.optional = 1

_I1.addField('a1', Attribute("This is an attribute"))

class _I1_(_I1): pass
class _I1__(_I1_): pass

class _I2(_I1__):
    def f21(): pass
    def f22(): pass
    f23 = f22


def test_suite():
    return unittest.makeSuite(InterfaceTests)

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__=="__main__":
    main()
