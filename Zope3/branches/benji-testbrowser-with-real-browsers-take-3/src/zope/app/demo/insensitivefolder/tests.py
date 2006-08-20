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
"""Tests for the case-insensitive Folder.

$Id$
"""
import unittest
from zope.app.container.tests import test_containertraverser  
from zope.app.demo.insensitivefolder import CaseInsensitiveContainerTraverser

class Container(test_containertraverser.TestContainer):

    def keys(self):
        return self.__dict__.keys()

    def __getitem__(self, name):
        return self.__dict__[name]


class InsensitiveCaseTraverserTest(test_containertraverser.TraverserTest):

    def _getTraverser(self, context, request):
        return CaseInsensitiveContainerTraverser(context, request)

    def _getContainer(self, **kw):
        return Container(**kw)
        
    def test_allLowerCaseItemTraversal(self):
        self.assertEquals(
            self.traverser.publishTraverse(self.request, 'foo'),
            self.foo)
        self.assertEquals(
            self.traverser.publishTraverse(self.request, 'foO'),
            self.foo)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(InsensitiveCaseTraverserTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
