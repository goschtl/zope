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
"""Functional tests for the Photo package

$Id: test_photo.py,v 1.2 2003/09/21 22:17:47 BjornT Exp $
"""

import unittest
from transaction import get_transaction
from zope.app.file.tests.test_image import zptlogo
from zope.app.traversing.api import traverseName
from zope.app.tests.functional import FunctionalTestCase

from photo import Photo


class TestPhoto(FunctionalTestCase):

    def setUp(self):
        FunctionalTestCase.setUp(self)
        rootFolder = self.getRootFolder()
        rootFolder['photo'] = Photo()

        get_transaction().commit()

    def tearDown(self):
        FunctionalTestCase.tearDown(self)

    def test_getImage_displayId(self):
        photo = traverseName(self.getRootFolder(), 'photo')
        photo.data = zptlogo
        self.assertEqual(zptlogo, photo.getImage('original').data)
        for displayId in photo.getDisplayIds():
            self.assertEqual(photo.getDisplaySize(displayId),
                             photo.getImage(displayId).getImageSize())

    def test_getImage_default(self):
        photo = traverseName(self.getRootFolder(), 'photo')
        photo.data = zptlogo
        self.assertEqual(zptlogo, photo.getImage('original').data)

        for displayId in photo.getDisplayIds():
            photo.currentDisplayId = displayId
            self.assertEqual(photo.getDisplaySize(displayId),
                             photo.getImage().getImageSize())
          


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPhoto))
    return suite


if __name__ == '__main__':
    unittest.main()
