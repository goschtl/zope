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
"""Functional tests for File.

$Id: ftests.py 25177 2004-06-02 13:17:31Z jim $
"""
import unittest
from xml.sax.saxutils import escape
from StringIO import StringIO

from zope.app.tests.functional import BrowserTestCase
from zope.app.file.file import File

class FileTest(BrowserTestCase):

    content = u'File <Data>' 

    def addFile(self):
        file = File(self.content)
        root = self.getRootFolder()
        root['file'] = file
        self.commit()

    def testAddForm(self):
        response = self.publish(
            '/+/zope.app.file.File=',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('Add a File' in body)
        self.assert_('Content Type' in body)
        self.assert_('Data' in body)
        self.assert_('Object Name' in body)
        self.assert_('"Add"' in body)
        self.checkForBrokenLinks(body, '/+/zope.app.file.File=',
                                 'mgr:mgrpw')

    def testAdd(self):
        response = self.publish(
            '/+/zope.app.file.File=',
            form={'type_name': u'zope.app.file.File',
                  'field.data': StringIO('A file'),
                  'add_input_name': u'file',
                  'UPDATE_SUBMIT': u'Add'},
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                         'http://localhost/@@contents.html')
        root = self.getRootFolder()
        self.assert_('file' in root)
        file = root['file']
        self.assertEqual(file.data, 'A file')

    def testEditForm(self):
        self.addFile()
        response = self.publish(
            '/file/@@edit.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('Change a file' in body)
        self.assert_('Content Type' in body)
        self.assert_('Data' in body)
        self.assert_(escape(self.content) in body)
        self.checkForBrokenLinks(body, '/file/@@edit.html', 'mgr:mgrpw')

    def testEdit(self):
        self.addFile()
        response = self.publish(
            '/file/@@edit.html',
            form={'field.data': u'<h1>A File</h1>',
                  'field.contentType': u'text/plain',
                  'UPDATE_SUBMIT': u'Edit'},
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('Change a file' in body)
        self.assert_('Content Type' in body)
        self.assert_('Data' in body)
        self.assert_(escape(u'<h1>A File</h1>') in body)
        root = self.getRootFolder()
        file = root['file']
        self.assertEqual(file.data, '<h1>A File</h1>')
        self.assertEqual(file.contentType, 'text/plain')

    def testUploadForm(self):
        self.addFile()
        response = self.publish(
            '/file/@@upload.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('Upload a file' in body)
        self.assert_('Content Type' in body)
        self.assert_('Data' in body)
        self.failIf(escape(self.content) in body)
        self.checkForBrokenLinks(body, '/file/@@upload.html', 'mgr:mgrpw')

    def testUpload(self):
        self.addFile()
        response = self.publish(
            '/file/@@upload.html',
            form={'field.data': StringIO('<h1>A file</h1>'),
                  'field.contentType': u'text/plain',
                  'UPDATE_SUBMIT': u'Change'},
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('Upload a file' in body)
        self.assert_('Content Type' in body)
        self.assert_('Data' in body)
        self.failIf(escape(u'<h1>A File</h1>') in body)
        root = self.getRootFolder()
        file = root['file']
        self.assertEqual(file.data, '<h1>A file</h1>')
        self.assertEqual(file.contentType, 'text/plain')
        
    def testIndex(self):
        self.addFile()
        response = self.publish(
            '/file/@@index.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assertEqual(body, self.content)
        self.checkForBrokenLinks(body, '/file/@@index.html', 'mgr:mgrpw')

    def testPreview(self):
        self.addFile()
        response = self.publish(
            '/file/@@preview.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('<iframe src="."' in body)
        self.checkForBrokenLinks(body, '/file/@@preview.html', 'mgr:mgrpw')



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(FileTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
