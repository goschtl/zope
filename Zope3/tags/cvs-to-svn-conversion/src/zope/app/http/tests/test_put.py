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
"""Test HTTP PUT verb

$Id: test_put.py,v 1.7 2004/03/15 13:10:52 srichter Exp $
"""
__metaclass__ = type

from unittest import TestCase, TestSuite, makeSuite
from StringIO import StringIO
import zope.app.http.put
from zope.publisher.browser import TestRequest
from zope.app.filerepresentation.interfaces import IWriteFile
from zope.app.filerepresentation.interfaces import IWriteDirectory, IFileFactory
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.interface import implements

class File:

    implements(IWriteFile)

    def __init__(self, name, content_type, data):
        self.name = name
        self.content_type = content_type
        self.data = data

    def write(self, data):
        self.data = data

class Container:

    implements(IWriteDirectory, IFileFactory)

    def __setitem__(self, name, object):
        setattr(self, name, object)

    def __call__(self, name, content_type, data):
        return File(name, content_type, data)


class TestNullPUT(PlacelessSetup, TestCase):

    def test(self):
        container = Container()
        content = "some content\n for testing"
        request = TestRequest(StringIO(content), StringIO(),
                              {'CONTENT_TYPE': 'test/foo',
                               'CONTENT_LENGTH': str(len(content)),
                               })
        null = zope.app.http.put.NullResource(container, 'spam')
        put = zope.app.http.put.NullPUT(null, request)
        self.assertEqual(getattr(container, 'spam', None), None)
        self.assertEqual(put.PUT(), '')
        request.response.setBody('')
        file = container.spam
        self.assertEqual(file.__class__, File)
        self.assertEqual(file.name, 'spam')
        self.assertEqual(file.content_type, 'test/foo')
        self.assertEqual(file.data, content)

        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 201)

    def test_bad_content_header(self):
        container = Container()
        content = "some content\n for testing"
        request = TestRequest(StringIO(content), StringIO(),
                              {'CONTENT_TYPE': 'test/foo',
                               'CONTENT_LENGTH': str(len(content)),
                               'HTTP_CONTENT_FOO': 'Bar',
                               })
        null = zope.app.http.put.NullResource(container, 'spam')
        put = zope.app.http.put.NullPUT(null, request)
        self.assertEqual(getattr(container, 'spam', None), None)
        self.assertEqual(put.PUT(), '')
        request.response.setBody('')

        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 501)

class TestFilePUT(PlacelessSetup, TestCase):

    def test(self):
        file = File("thefile", "text/x", "initial content")
        content = "some content\n for testing"
        request = TestRequest(StringIO(content), StringIO(),
                              {'CONTENT_TYPE': 'test/foo',
                               'CONTENT_LENGTH': str(len(content)),
                               })
        put = zope.app.http.put.FilePUT(file, request)
        self.assertEqual(put.PUT(), '')
        request.response.setBody('')
        self.assertEqual(file.data, content)

    def test_bad_content_header(self):
        file = File("thefile", "text/x", "initial content")
        content = "some content\n for testing"
        request = TestRequest(StringIO(content), StringIO(),
                              {'CONTENT_TYPE': 'test/foo',
                               'CONTENT_LENGTH': str(len(content)),
                               'HTTP_CONTENT_FOO': 'Bar',
                               })
        put = zope.app.http.put.FilePUT(file, request)
        self.assertEqual(put.PUT(), '')
        request.response.setBody('')
        self.assertEqual(file.data, "initial content")

        # Check HTTP Response
        self.assertEqual(request.response.getStatus(), 501)

def test_suite():
    return TestSuite((
        makeSuite(TestFilePUT),
        makeSuite(TestNullPUT),
        ))
