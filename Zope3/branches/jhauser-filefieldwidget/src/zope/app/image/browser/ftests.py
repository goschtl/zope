##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Functional tests for Image.

$Id: ftests.py 25177 2004-06-02 13:17:31Z jim $
"""
import unittest
from StringIO import StringIO

from zope.app.tests.functional import BrowserTestCase
from zope.app.file.image import Image
from zope.app.image.tests.test_image import zptlogo


class ImageTest(BrowserTestCase):

    content = zptlogo

    def addImage(self):
        image = Image(self.content)
        root = self.getRootFolder()
        root['image'] = image
        self.commit()

    def testAddForm(self):
        response = self.publish(
            '/+/zope.app.image.Image=',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('Add an Image' in body)
        self.assert_('Content Type' in body)
        self.assert_('Data' in body)
        self.assert_('Object Name' in body)
        self.assert_('"Add"' in body)
        self.checkForBrokenLinks(body, '/+/zope.app.image.Image=',
                                 'mgr:mgrpw')

    def testAdd(self):
        response = self.publish(
            '/+/zope.app.image.Image=',
            form={'type_name': u'zope.app.image.Image',
                  'field.data': StringIO(self.content),
                  'add_input_name': u'image',
                  'UPDATE_SUBMIT': u'Add'},
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                         'http://localhost/@@contents.html')
        root = self.getRootFolder()
        self.assert_('image' in root)
        image = root['image']
        self.assertEqual(image.data, self.content)

    def testUploadForm(self):
        self.addImage()
        response = self.publish(
            '/image/@@upload.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('Upload an image' in body)
        self.assert_('Content Type' in body)
        self.assert_('Data' in body)
        self.assert_('1 KB 16x16' in body)
        self.checkForBrokenLinks(body, '/image/@@upload.html', 'mgr:mgrpw')

    def testUpload(self):
        self.addImage()
        response = self.publish(
            '/image/@@upload.html',
            form={'field.data': StringIO(''),
                  'UPDATE_SUBMIT': u'Change'},
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('Upload an image' in body)
        self.assert_('Content Type' in body)
        self.assert_('Data' in body)
        self.assert_('0 KB ?x?' in body)
        root = self.getRootFolder()
        image = root['image']
        self.assertEqual(image.data, '')
        self.assertEqual(image.contentType, 'image/gif')
        
    def testIndex(self):
        self.addImage()
        response = self.publish(
            '/image/@@index.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertEqual(body, self.content)
        self.checkForBrokenLinks(body, '/image/@@index.html', 'mgr:mgrpw')

    def testPreview(self):
        self.addImage()
        response = self.publish(
            '/image/@@preview.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('<iframe src="."' in body)
        self.checkForBrokenLinks(body, '/image/@@preview.html', 'mgr:mgrpw')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ImageTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
