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
"""Unit tests for ImageMagickUtility

$Id: test_imagemagickutility.py,v 1.1 2003/08/15 12:10:56 BjornT Exp $
"""

import unittest

from zope.interface.verify import verifyObject
from photo.utilities import ImageMagickUtility
from photo.interfaces import IImageMagickUtility
from photo.tests.test_iimageresizeutility import \
     TestIImageResizeUtility

class TestImageMagickUtility(TestIImageResizeUtility):

    def _makeImageResizer(self):
        return ImageMagickUtility()

    def test_implementation(self):
        utility = ImageMagickUtility()
        verifyObject(IImageMagickUtility, utility)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestImageMagickUtility))
    return suite


if __name__ == '__main__':
    unittest.main()
