##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Unit tests for HelloPDF.

$Id: test_hellomodule.py,v 1.1 2003/12/16 09:27:18 nmurthy Exp $
"""

import unittest
from zope.interface.verify import verifyObject

class TestHelloModule(unittest.TestCase):

    def test_interface(self):
        from zope.products.hellopackage.interfaces import IHello
        from zope.products.hellopackage.hellomodule import HelloClass
        verifyObject(IHello, HelloClass())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestHelloModule))
    return suite


if __name__ == '__main__':
    unittest.main()
