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
"""XML Navigation Tree Tests

$Id$
"""
from unittest import TestCase, TestLoader, TextTestRunner

from zope.interface import implements
from zope.pagetemplate.tests.util import check_xml
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPublisher

from zope.app.tests import ztapi
from zope.app.traversing.api import traverse
from zope.app.container.interfaces import IReadContainer

from zope.app.rotterdam.tests import util
from zope.app.rotterdam.xmlobject import ReadContainerXmlObjectView
from zope.app.rotterdam.xmlobject import XmlObjectView

from zope.app.site.tests.placefulsetup import PlacefulSetup

class File(object):
    pass

class TestXmlObject(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self, site=True)
        self.createStandardServices()

    def testXMLTreeViews(self):
        rcxov = ReadContainerXmlObjectView
        treeView = rcxov(self.folder1, TestRequest()).singleBranchTree
        check_xml(treeView(), util.read_output('test1.xml'))

        treeView = rcxov(self.folder1, TestRequest()).children
        check_xml(treeView(), util.read_output('test2.xml'))

        treeView = rcxov(self.folder1_1_1, TestRequest()).children
        check_xml(treeView(), util.read_output('test3.xml'))

        treeView = rcxov(self.rootFolder, TestRequest()).children
        check_xml(treeView(), util.read_output('test4.xml'))

        file1 = File()
        self.folder1_1_1["file1"] = file1
        self.file1 = traverse(self.rootFolder,
                              '/folder1/folder1_1/folder1_1_1/file1')

        class ReadContainerView(ReadContainerXmlObjectView):
            implements(IBrowserPublisher)
            def browserDefault(self, request):
                return self, ()
            def publishTraverse(self, request, name):
                raise NotFoundError(self, name, request)
            def __call__(self):
                return self.singleBranchTree()

        ztapi.browserView(IReadContainer, 'singleBranchTree.xml',
                          ReadContainerView)

        treeView = rcxov(self.folder1_1_1, TestRequest()).singleBranchTree
        check_xml(treeView(), util.read_output('test5.xml'))

        treeView = XmlObjectView(self.file1, TestRequest()).singleBranchTree
        check_xml(treeView(), util.read_output('test5.xml'))


def test_suite():
    loader = TestLoader()
    return loader.loadTestsFromTestCase(TestXmlObject)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
