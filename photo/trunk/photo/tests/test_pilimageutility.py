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
"""Unit tests for PILImageUtility

$Id: test_pilimageutility.py,v 1.1 2003/08/15 12:10:56 BjornT Exp $
"""

import unittest

from zope.interface.verify import verifyObject
from photo.utilities import PILImageUtility
from photo.interfaces import IPILImageUtility
from photo.tests.test_iimageresizeutility import TestIImageResizeUtility

class TestPILImageUtility(TestIImageResizeUtility):

    def _makeImageResizer(self):
        return PILImageUtility()

    def test_implementation(self):
        utility = PILImageUtility()
        verifyObject(IPILImageUtility, utility)

    def test_getNewSizeKeepAspect(self):
        util = PILImageUtility()
        self.assertEqual(util._getNewSize((10, 10), (25, 50), 1),
                         (25, 25))
        self.assertEqual(util._getNewSize((10, 10), (50, 25), 1),
                         (25, 25))
        self.assertEqual(util._getNewSize((50, 50), (25, 50), 1),
                         (25, 25))
        self.assertEqual(util._getNewSize((50, 50), (50, 25), 1),
                         (25, 25))

    def test_getNewSizeDontKeepAspect(self):
        util = PILImageUtility()
        self.assertEqual(util._getNewSize((10, 10), (25, 50), 0),
                         (25, 50))
        self.assertEqual(util._getNewSize((10, 10), (50, 25), 0),
                         (50, 25))
        self.assertEqual(util._getNewSize((50, 50), (25, 50), 0),
                         (25, 50))
        self.assertEqual(util._getNewSize((50, 50), (50, 25), 0),
                         (50, 25))



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPILImageUtility))
    return suite


if __name__ == '__main__':
    unittest.main()
