##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Tests for the IPhoto namespace

$Id: tests.py,v 1.1.1.1 2004/02/18 18:07:08 srichter Exp $
"""
import unittest
from zope.interface import classImplements
from zope.testing.doctestunit import DocTestSuite
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.file.image import Image
from zope.app.file.interfaces import IImage
from zope.app.tests import ztapi, placelesssetup, setup
from book.photodavns.interfaces import IPhoto
from book.photodavns import ImagePhotoNamespace

def setUp(test):
    placelesssetup.setUp()
    ztapi.provideAdapter(IImage, IPhoto, ImagePhotoNamespace)
    setup.setUpAnnotations()
    classImplements(Image, IAttributeAnnotatable)

def test_suite():
    return unittest.TestSuite((
        DocTestSuite('book.photodavns',
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
