##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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
from cStringIO import StringIO
from zope.testing import doctest, renormalizing
import bozo.reuse
import re
import unittest
import zope.publisher.tests.test_browserrequest

class BozoBrowserTests(zope.publisher.tests.test_browserrequest.BrowserTests):

    def _createRequest(self, extra_env={}, body=""):
        env = self._testEnv.copy()
        env.update(extra_env)
        if len(body):
            env['CONTENT_LENGTH'] = str(len(body))

        publication = zope.publisher.tests.test_browserrequest.Publication(
            self.app)
        request = bozo.reuse.Request(StringIO(body), env)
        request.setPublication(publication)
        return request

    def testHeaders(self):
        headers = {
            'HTTP_TEST_HEADER': 'test',
            'Another-Test': 'another',
        }
        req = self._createRequest(extra_env=headers)
        self.assertEquals(req.headers[u'TEST-HEADER'], u'test')
        self.assertEquals(req.headers[u'test-header'], u'test')
        self.assertEquals(req.getHeader('TEST_HEADER', literal=True), u'test')
        self.assertEquals(req.getHeader('TEST-HEADER', literal=True), None)
        self.assertEquals(req.getHeader('test_header', literal=True), None)
        self.assertEquals(req.getHeader('Another-Test', literal=True),
                          'another')

    def testIssue559(self):
        extra = {'QUERY_STRING': 'HTTP_REFERER=peter',
                 'HTTP_REFERER':'http://localhost/',
                 'PATH_INFO': '/folder/item3/'}
        request = self._createRequest(extra)
        zope.publisher.tests.test_browserrequest.publish(request)
        self.assertEqual(request.headers.get('Referer'), 'http://localhost/')
        self.assertEqual(request.form, {u'HTTP_REFERER': u'peter'})

class BozoAPITests(zope.publisher.tests.test_browserrequest.BrowserTests):

    def _Test__new(self, environ=None, **kw):
        if environ is None:
            environ = kw
        return bozo.reuse.Request(StringIO(''), environ)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(BozoBrowserTests),
        unittest.makeSuite(BozoAPITests),
        doctest.DocFileSuite(
            'doc/request.test',
            checker=renormalizing.RENormalizing([
                (re.compile('0x[a-fA-F0-9]+'), 'ADDR'),
                ]),
            ),
        ))


