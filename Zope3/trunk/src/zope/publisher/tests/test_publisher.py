##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

$Id: test_publisher.py,v 1.3 2003/03/13 18:49:15 alga Exp $
"""

import unittest

from zope.publisher.publish import publish
from zope.publisher.base import BaseRequest
from zope.publisher.base import DefaultPublication
from zope.publisher.interfaces import Retry, Unauthorized, NotFound, DebugError
from zope.publisher.interfaces import IPublication

from zope.interface.verify import verifyClass
from zope.interface.implements import instancesOfObjectImplements

from StringIO import StringIO

class TestPublication(DefaultPublication):
    # Override handleException to reraise for testing purposes
    def handleException(self, object, request, exc_info, retry_allowed=1):
        raise exc_info[0], exc_info[1], exc_info[2]

class PublisherTests(unittest.TestCase):
    def setUp(self):
        class AppRoot:
            " "

        class Folder:
            " "

        class Item:
            " "
            def __call__(self):
                return "item"

        class NoDocstringItem:
            def __call__(self):
                return "Yo! No docstring!"

        self.app = AppRoot()
        self.app.folder = Folder()
        self.app.folder.item = Item()

        self.app._item = Item()
        self.app.noDocString = NoDocstringItem()

    def _createRequest(self, path, outstream=None, **kw):
        if outstream is None:
            outstream = StringIO()
        publication = TestPublication(self.app)
        path = path.split('/')
        path.reverse()
        request = BaseRequest(StringIO(''), outstream, kw)
        request.setTraversalStack(path)
        request.setPublication(publication)
        return request

    def _publisherResults(self, path, **kw):
        outstream = StringIO()
        request = self._createRequest(path, outstream=outstream, **kw)
        publish(request, handle_errors=0)
        return outstream.getvalue()

    def testImplementsIPublication(self):
        self.failUnless(IPublication.isImplementedBy(
                            DefaultPublication(self.app)))

    def testInterfacesVerify(self):
        for interface in instancesOfObjectImplements(DefaultPublication):
            verifyClass(interface, DefaultPublication)

    def testTraversalToItem(self):
        res = self._publisherResults('/folder/item')
        self.failUnlessEqual(res, 'item')
        res = self._publisherResults('/folder/item/')
        self.failUnlessEqual(res, 'item')
        res = self._publisherResults('folder/item')
        self.failUnlessEqual(res, 'item')

    def testUnderscoreUnauthorizedException(self):
        self.assertRaises(Unauthorized, self._publisherResults, '/_item')

    def testNotFoundException(self):
        self.assertRaises(NotFound, self._publisherResults, '/foo')

    def testDebugError(self):
        self.assertRaises(DebugError, self._publisherResults, '/noDocString')

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(PublisherTests)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
