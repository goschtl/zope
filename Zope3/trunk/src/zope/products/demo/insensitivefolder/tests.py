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

$Id: tests.py,v 1.1 2004/02/13 23:28:45 srichter Exp $
"""
import unittest
from zope.component.tests.request import Request
from zope.component.servicenames import Presentation
from zope.products.demo.insensitivefolder import CaseInsensitiveContainerTraverser
from zope.interface import Interface, implements
from zope.exceptions import NotFoundError
from zope.app import zapi
from zope.app.interfaces.container import IContainer
from zope.app.tests.placelesssetup import PlacelessSetup

class I(Interface):
    pass


class Container:
    implements(IContainer)

    def __init__(self, **kw):
        for k in kw:
            setattr(self, k , kw[k])

    def get(self, name, default=None):
        return getattr(self, name, default)

    def keys(self):
        return self.__dict__.keys()

    def __getitem__(self, name):
        return self.__dict__[name]

class Request(Request):
    def getEffectiveURL(self):
        return ''


class View:
    def __init__(self, comp, request):
        self._comp = comp


class Test(PlacelessSetup, unittest.TestCase):

    def testAttr(self):
        # test container traverse
        foo = Container()
        c   = Container(foo=foo)
        req = Request(I, '')

        T = CaseInsensitiveContainerTraverser(c, req)
        self.failUnless(T.publishTraverse(req,'foo') is foo)
        self.failUnless(T.publishTraverse(req,'foO') is foo)
        self.assertRaises(NotFoundError , T.publishTraverse, req ,'morebar')


    def testView(self):
        # test getting a view
        foo = Container()
        c   = Container(foo=foo)
        req = Request(I, '')

        T = CaseInsensitiveContainerTraverser(c, req)
        zapi.getService(None, Presentation).provideView(
            IContainer, 'viewfoo', I, [View])

        self.failUnless(T.publishTraverse(req,'viewfoo').__class__ is View )
        self.failUnless(T.publishTraverse(req,'foo') is foo)

        self.assertRaises(NotFoundError , T.publishTraverse, req, 'morebar')
        self.assertRaises(NotFoundError , T.publishTraverse, req,
                          '@@morebar')


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
