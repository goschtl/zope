##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""Tests for the case-insensitive Folder.

$Id: tests.py,v 1.2 2004/02/14 02:27:40 srichter Exp $
"""
import unittest
from zope.app import zapi
from zope.app.interfaces.container import IReadContainer
from zope.app.tests import ztapi
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.tests.request import Request
from zope.exceptions import NotFoundError
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.products.demo.insensitivefolder import \
     CaseInsensitiveContainerTraverser

class Container:
    implements(IReadContainer)

    def __init__(self, **kw):
        for k in kw:
            setattr(self, k , kw[k])

    def get(self, name, default=None):
        return getattr(self, name, default)

    def keys(self):
        return self.__dict__.keys()

    def __getitem__(self, name):
        return self.__dict__[name]


class View:
    def __init__(self, context, request):
        self.context = context
        self.request = request


class TraverserTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TraverserTest, self).setUp()
        self.foo = Container()
        foo2 = Container(foo=self.foo)
        self.request = Request(IBrowserRequest, '')
        self.traverser = CaseInsensitiveContainerTraverser(foo2, self.request)
        ztapi.browserView(IReadContainer, 'viewfoo', [View])
        
    def test_itemTraversal(self):
        self.assertEquals(
            self.traverser.publishTraverse(self.request, 'foo'),
            self.foo)
        self.assertEquals(
            self.traverser.publishTraverse(self.request, 'foO'),
            self.foo)
        self.assertRaises(
            NotFoundError,
            self.traverser.publishTraverse, self.request, 'morebar')

    def test_viewTraversal(self):
        self.assertEquals(
            self.traverser.publishTraverse(self.request, 'viewfoo').__class__,
            View)
        self.assertEquals(
            self.traverser.publishTraverse(self.request, 'foo'),
            self.foo)
        self.assertRaises(
            NotFoundError,
            self.traverser.publishTraverse, self.request, 'morebar')
        self.assertRaises(
            NotFoundError,
            self.traverser.publishTraverse, self.request, '@@morebar')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TraverserTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
