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
from zope.testing.doctestunit import DocTestSuite
from zope.component import getAdapter
from zope.app.tests import ztapi
from zope.app.traversing import traverse
from zope.app.interfaces.dublincore import IZopeDublinCore
from zope.app.interfaces.content.folder import IFolder
from zope.app.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.component.tests.test_servicemanagercontainer \
     import BaseTestServiceManagerContainer
from zope.app.container.tests.test_icontainer import BaseTestIContainer
from zope.app.container.tests.test_icontainer import DefaultTestData
from zope.app import content


class Test(BaseTestIContainer, BaseTestServiceManagerContainer, TestCase):

    def makeTestObject(self):
        from zope.app.content.folder import Folder
        return Folder()

    def makeTestData(self):
        return DefaultTestData()

    def getUnknownKey(self):
        return '10'

    def getBadKeyTypes(self):
        return [None, ['foo'], 1, '\xf3abc']


class FolderMetaDataTest(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        PlacefulSetup.buildFolders(self)
        ztapi.provideAdapter(IFolder, IZopeDublinCore, ZDCAnnotatableAdapter)

def test_suite():
    return TestSuite((
        makeSuite(Test),
        makeSuite(FolderMetaDataTest),
        DocTestSuite('zope.app.content'),
        ))    

if __name__=='__main__':
    main(defaultTest='test_suite')
