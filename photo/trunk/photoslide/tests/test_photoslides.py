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
"""Tests for the PhotoSlideFolder class

$Id: test_photoslides.py,v 1.1 2003/08/15 12:15:22 BjornT Exp $
"""

import unittest

from zope.app.container.tests.test_icontainer import BaseTestIContainer
from zope.app.container.tests.test_icontainer import DefaultTestData
from zope.app.file.tests.test_image import zptlogo
from zope.app.file.image import Image
from zope.interface.verify import verifyObject
from zope.app import zapi

small_image = Image(zptlogo)

class TestPhotoSlideFolder(BaseTestIContainer, unittest.TestCase):

    def makeTestObject(self):
        from photoslide import PhotoSlideFolder
        return PhotoSlideFolder()

    def getUnknownKey(self):
        return 'm'

    def getBadKeyTypes(self):
        return [None, ['foo'], 1, '\xf3abc']

    def makeTestData(self):
        return DefaultTestData()

    def test_interface(self):
        from photoslide.interfaces import IPhotoSlideFolder
        from photoslide import PhotoSlideFolder

        verifyObject(IPhotoSlideFolder, PhotoSlideFolder())



def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPhotoSlideFolder))
    return suite


if __name__ == '__main__':
    unittest.main()
