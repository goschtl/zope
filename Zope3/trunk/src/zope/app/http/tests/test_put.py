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
"""
$Id: test_put.py,v 1.1 2003/02/07 15:59:38 jim Exp $
"""
__metaclass__ = type

from unittest import TestCase, TestSuite, main, makeSuite
from StringIO import StringIO
import zope.app.http.put
from zope.publisher.browser import TestRequest
from zope.app.interfaces.file import IWriteFile, IWriteDirectory, IFileFactory
from zope.app.interfaces.container import IZopeWriteContainer
from zope.app.tests.placelesssetup import PlacelessSetup

class File:

    __implements__ = IWriteFile

    def __init__(self, name, content_type, data):
        self.name = name
        self.content_type = content_type
        self.data = data

    def write(self, data):
        self.data = data

class Container:

    __implements__ = IWriteDirectory, IZopeWriteContainer, IFileFactory

    def setObject(self, name, object):
        setattr(self, name, object)

    def __call__(self, name, content_type, data):
        return File(name, content_type, data)
        

class TestNullPUT(PlacelessSetup, TestCase):

    def test(self):
        container = Container()
        content = "some content\n for testing"
        request = TestRequest(StringIO(content), StringIO(),
                              {'CONTENT_TYPE': 'test/foo'})
        null = zope.app.http.put.NullResource(container, 'spam')
        put = zope.app.http.put.NullPUT(null, request)
        self.assertEqual(getattr(container, 'spam', None), None)
        self.assertEqual(put.PUT(), '')
        file = container.spam
        self.assertEqual(file.__class__, File)
        self.assertEqual(file.name, 'spam')
        self.assertEqual(file.content_type, 'test/foo')
        self.assertEqual(file.data, content)        

class TestFilePUT(PlacelessSetup, TestCase):

    def test(self):
        file = File("thefile", "text/x", "initial content")
        content = "some content\n for testing"
        request = TestRequest(StringIO(content), StringIO(),
                              {'CONTENT_TYPE': 'test/foo'})
        put = zope.app.http.put.FilePUT(file, request)
        self.assertEqual(put.PUT(), '')
        self.assertEqual(file.data, content)        

def test_suite():
    return TestSuite((
        makeSuite(TestFilePUT),
        makeSuite(TestNullPUT),
        ))
