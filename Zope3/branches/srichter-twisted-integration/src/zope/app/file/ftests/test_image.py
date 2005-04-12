##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""File Functional Tests

$Id$
"""
import unittest
import cgi
from cStringIO import StringIO
from zope.app.testing.functional import BrowserTestCase
from zope.publisher.browser import FileUpload

zptlogo = (
    'GIF89a\x10\x00\x10\x00\xd5\x00\x00\xff\xff\xff\xff\xff\xfe\xfc\xfd\xfd'
    '\xfa\xfb\xfc\xf7\xf9\xfa\xf5\xf8\xf9\xf3\xf6\xf8\xf2\xf5\xf7\xf0\xf4\xf6'
    '\xeb\xf1\xf3\xe5\xed\xef\xde\xe8\xeb\xdc\xe6\xea\xd9\xe4\xe8\xd7\xe2\xe6'
    '\xd2\xdf\xe3\xd0\xdd\xe3\xcd\xdc\xe1\xcb\xda\xdf\xc9\xd9\xdf\xc8\xd8\xdd'
    '\xc6\xd7\xdc\xc4\xd6\xdc\xc3\xd4\xda\xc2\xd3\xd9\xc1\xd3\xd9\xc0\xd2\xd9'
    '\xbd\xd1\xd8\xbd\xd0\xd7\xbc\xcf\xd7\xbb\xcf\xd6\xbb\xce\xd5\xb9\xcd\xd4'
    '\xb6\xcc\xd4\xb6\xcb\xd3\xb5\xcb\xd2\xb4\xca\xd1\xb2\xc8\xd0\xb1\xc7\xd0'
    '\xb0\xc7\xcf\xaf\xc6\xce\xae\xc4\xce\xad\xc4\xcd\xab\xc3\xcc\xa9\xc2\xcb'
    '\xa8\xc1\xca\xa6\xc0\xc9\xa4\xbe\xc8\xa2\xbd\xc7\xa0\xbb\xc5\x9e\xba\xc4'
    '\x9b\xbf\xcc\x98\xb6\xc1\x8d\xae\xbaFgs\x00\x00\x00\x00\x00\x00\x00\x00'
    '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    '\x00,\x00\x00\x00\x00\x10\x00\x10\x00\x00\x06z@\x80pH,\x12k\xc8$\xd2f\x04'
    '\xd4\x84\x01\x01\xe1\xf0d\x16\x9f\x80A\x01\x91\xc0ZmL\xb0\xcd\x00V\xd4'
    '\xc4a\x87z\xed\xb0-\x1a\xb3\xb8\x95\xbdf8\x1e\x11\xca,MoC$\x15\x18{'
    '\x006}m\x13\x16\x1a\x1f\x83\x85}6\x17\x1b $\x83\x00\x86\x19\x1d!%)\x8c'
    '\x866#\'+.\x8ca`\x1c`(,/1\x94B5\x19\x1e"&*-024\xacNq\xba\xbb\xb8h\xbeb'
    '\x00A\x00;'
    )

class TestFile(BrowserTestCase):

    def _setupImage(self):
        response = self.publish('/+/action.html',
                                basic='mgr:mgrpw',
                                form={'type_name': u'zope.app.content.Image',
                                      'id': u'img'})

        fs = cgi.FieldStorage()
        fs.name = 'field.data'
        fs.value = 'test.gif'
        fs.filename = 'test.gif'
        fs.file = StringIO(zptlogo)
        response = self.publish('/img/@@upload.html',
                                basic='mgr:mgrpw',
                                form={'field.data': FileUpload(fs),
                                      'field.contentType': u'image/gif',
                                      'UPDATE_SUBMIT': 'Change'})
        

    def testAddImage(self):
        # Step 1: add the image
        response = self.publish('/+/action.html',
                                basic='mgr:mgrpw',
                                form={'type_name': u'zope.app.content.Image',
                                      'id': u'img'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                         'http://localhost/@@contents.html')
        # Step 2: check that it it visible in the folder listing
        response = self.publish('/')
        self.assertEqual(response.getStatus(), 200)
        self.assert_(response.getBody().find('img') != -1)
        # Step 3: check that its contents are available
        response = self.publish('/img')
        self.assertEqual(response.getStatus(), 200)


    def testImageUpload(self):
        self._setupImage()

        root = self.getRootFolder()
        self.assertEqual(root['img'].contentType, u'image/gif')
        self.assertEqual(root['img'].data, zptlogo)


    def testImageUploadOnlyChangingContentType(self):
        self._setupImage()

        response = self.publish('/img/@@upload.html',
                                basic='mgr:mgrpw',
                                form={'field.contentType': u'image/gif2',
                                      'UPDATE_SUBMIT': u'Change'})
        
        root = self.getRootFolder()
        self.assertEqual(root['img'].contentType, u'image/gif2')
        self.assertEqual(root['img'].data, zptlogo)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFile))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
