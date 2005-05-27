##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Tests for zope.app.tests.functional."""

import StringIO
import unittest

import zope.app.tests.functional


HEADERS = """\
HTTP/1.1 200 Ok
Content-Type: text/plain
"""

BODY = """\
This is the response body.
"""

class DocResponseWrapperTestCase(unittest.TestCase):

    def setUp(self):
        self.body_output = StringIO.StringIO()
        self.path = "/foo/bar/"
        self.response = object()

        self.wrapper = zope.app.tests.functional.DocResponseWrapper(
            self.response, self.body_output, self.path, HEADERS)

    def test__str__(self):
        self.assertEqual(str(self.wrapper),
                         HEADERS + "\n")
        self.body_output.write(BODY)
        self.assertEqual(str(self.wrapper),
                         "%s\n\n%s" % (HEADERS, BODY))

    def test_getBody(self):
        self.assertEqual(self.wrapper.getBody(), "")
        self.body_output.write(BODY)
        self.assertEqual(self.wrapper.getBody(), BODY)

    def test_getOutput(self):
        self.assertEqual(self.wrapper.getOutput(), "")
        self.body_output.write(BODY)
        self.assertEqual(self.wrapper.getOutput(), BODY)

class AuthHeaderTestCase(unittest.TestCase):

    def test_auth_encoded(self):
        auth_header = zope.app.tests.functional.auth_header
        header = 'Basic Z2xvYmFsbWdyOmdsb2JhbG1ncnB3'
        self.assertEquals(auth_header(header), header)

    def test_auth_non_encoded(self):
        auth_header = zope.app.tests.functional.auth_header
        header = 'Basic globalmgr:globalmgrpw'
        expected = 'Basic Z2xvYmFsbWdyOmdsb2JhbG1ncnB3'
        self.assertEquals(auth_header(header), expected)

    def test_auth_non_encoded_empty(self):
        auth_header = zope.app.tests.functional.auth_header
        header = 'Basic globalmgr:'
        expected = 'Basic Z2xvYmFsbWdyOg=='
        self.assertEquals(auth_header(header), expected)
        header = 'Basic :pass'
        expected = 'Basic OnBhc3M='
        self.assertEquals(auth_header(header), expected)

    def test_auth_non_encoded_colon(self):
        auth_header = zope.app.tests.functional.auth_header
        header = 'Basic globalmgr:pass:pass'
        expected = 'Basic Z2xvYmFsbWdyOnBhc3M6cGFzcw=='
        self.assertEquals(auth_header(header), expected)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DocResponseWrapperTestCase))
    suite.addTest(unittest.makeSuite(AuthHeaderTestCase))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
