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
from unittest import TestCase, TestSuite, main, makeSuite
from zope.component import getAdapter
from zope.component.adapter import provideAdapter
from zope.app.traversing import traverse
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.content.folder import IFolder
from zope.app.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.component.tests.test_servicemanagercontainer \
     import BaseTestServiceManagerContainer
from zope.app.container.tests.test_icontainer import BaseTestIContainer
from zope.app.container.tests.test_icontainer import DefaultTestData
from zope.app.interfaces.content.folder import ICloneWithoutChildren

class Test(BaseTestIContainer, BaseTestServiceManagerContainer, TestCase):

    def makeTestObject(self):
        from zope.app.content.folder import Folder
        return Folder()

    def makeTestData(self):
        return DefaultTestData()

    def test_cloneWithoutChildren(self):
        folder = self.makeTestObject()
        self.failUnless(ICloneWithoutChildren.isImplementedBy(folder))

        data = self.makeTestData()
        objects = [ data[i][1] for i in range(4) ]
        folder.setObject('foo', objects[0])
        folder.setObject('bar', objects[1])
        folder.setObject('baz', objects[2])
        folder.setObject('bam', objects[3])

        new_folder = folder.cloneWithoutChildren()

        self.failIf(new_folder is folder)

        self.assertEquals(len(new_folder.keys()), 0)
        self.failIf('foo' in new_folder.keys())
        self.failIf('bar' in new_folder.keys())
        self.failIf('baz' in new_folder.keys())
        self.failIf('bam' in new_folder.keys())

        self.assertEquals(len(new_folder.values()), 0)
        self.failIf(objects[0] in new_folder.values())
        self.failIf(objects[1] in new_folder.values())
        self.failIf(objects[2] in new_folder.values())
        self.failIf(objects[3] in new_folder.values())

        del folder['foo']
        del folder['bar']
        del folder['baz']
        del folder['bam']


class FolderMetaDataTest(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        provideAdapter(IFolder, IZopeDublinCore, ZDCAnnotatableAdapter)

    def test_cloneWithoutChildrenMetadata(self):
        root = self.rootFolder
        folder = traverse(root, 'folder1')
        self.failUnless(ICloneWithoutChildren.isImplementedBy(folder))
        getAdapter(folder, IZopeDublinCore).title = u'foo'
        getAdapter(folder, IZopeDublinCore).description = u'bar'

        new_folder = folder.cloneWithoutChildren()

        self.assertEquals(getAdapter(new_folder, IZopeDublinCore).title, u'foo')
        self.assertEquals(getAdapter(new_folder, IZopeDublinCore).description, u'bar')

def test_suite():
    return TestSuite((
        makeSuite(Test),
        makeSuite(FolderMetaDataTest),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
