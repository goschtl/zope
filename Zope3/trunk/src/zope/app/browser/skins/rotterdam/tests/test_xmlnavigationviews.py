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

Revision information:
$Id: test_xmlnavigationviews.py,v 1.4 2003/01/02 15:03:21 stevea Exp $
"""

#import sys
#sys.path.insert(0, r"c:\Zope3\src")


from unittest import TestCase, TestLoader, TextTestRunner
from zope.app.services.tests.eventsetup import EventSetup
from zope.pagetemplate.tests.util import check_xml
from zope.app.browser.skins.rotterdam.tests import util
from zope.app.browser.skins.rotterdam.xmlobject \
    import ReadContainerXmlObjectView
from zope.app.interfaces.container import IReadContainer
from zope.app.browser.skins.rotterdam.xmlobject import XmlObjectView
from zope.publisher.browser import TestRequest

class TestXmlObject(EventSetup, TestCase):
    
    def setUp(self):
        EventSetup.setUp(self)

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

        treeView = rcxov(self.folder1_1_1, TestRequest()).singleBranchTree
        check_xml(treeView(), util.read_output('test5.xml'))

        from zope.app.content.file import File
        from zope.proxy.context import ContextWrapper
        file1 = File()
        self.rootFolder.setObject("file1", self.folder1_1_1)
        self.file1 = ContextWrapper(file1, self.folder1_1_1, name = "file1")
        from zope.component.view import provideView
        from zope.publisher.interfaces.browser import IBrowserPresentation
        from zope.publisher.interfaces.browser import IBrowserPublisher
        class ReadContainerView(ReadContainerXmlObjectView):
            __implements__ = (IBrowserPublisher, 
                              ReadContainerXmlObjectView.__implements__)
            def browserDefault(self, request):
                return self, ()
            def publishTraverse(self, request, name):
                raise NotFoundError(self, name, request)
            def __call__(self):
                return self.singleBranchTree()
        provideView(IReadContainer, 'singleBranchTree.xml',
                    IBrowserPresentation, ReadContainerView)
        treeView = XmlObjectView(self.file1, TestRequest()).singleBranchTree
        #check_xml(treeView(), util.read_output('test5.xml'))


def test_suite():
    loader = TestLoader()
    return loader.loadTestsFromTestCase(TestXmlObject)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
