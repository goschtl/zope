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
$Id: placefulsetup.py,v 1.3 2002/12/28 14:13:28 stevea Exp $
"""
from zope import component as CA
from zope.component.adapter import provideAdapter
from zope.component.view import provideView
from zope.publisher.interfaces.browser import IBrowserPresentation

from zope.app.browser.absoluteurl import SiteAbsoluteURL, AbsoluteURL
from zope.app.component import hooks
from zope.app.container.traversal import ContainerTraversable
from zope.app.interfaces.container import ISimpleReadContainer
from zope.app.interfaces.content.folder import IRootFolder
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.interfaces.traversing import IPhysicallyLocatable
from zope.app.interfaces.traversing import ITraverser
from zope.app.interfaces.traversing import ITraversable
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.traversing.defaulttraversable import DefaultTraversable
from zope.app.traversing.etcnamespace import etc
from zope.app.traversing.namespaces import provideNamespaceHandler
from zope.app.traversing.physicallocationadapters \
     import WrapperPhysicallyLocatable, RootPhysicallyLocatable
from zope.app.traversing.traverser import Traverser


class PlacefulSetup(PlacelessSetup):

    def setUp(self):
        PlacelessSetup.setUp(self)
        # set up placeful hooks, saving originals for tearDown
        self.__old_getServiceManager_hook = CA.getServiceManager_hook
        CA.getServiceManager_hook = hooks.getServiceManager_hook
        self.setUpTraversal()

    def setUpTraversal(self):

        provideAdapter(None, ITraverser, Traverser)
        provideAdapter(None, ITraversable, DefaultTraversable)

        provideAdapter(
            ISimpleReadContainer, ITraversable, ContainerTraversable)
        provideAdapter(
            None, IPhysicallyLocatable, WrapperPhysicallyLocatable)
        provideAdapter(
            IContainmentRoot, IPhysicallyLocatable, RootPhysicallyLocatable)

        # set up etc namespace
        provideNamespaceHandler("etc", etc)

        provideView(None, "absolute_url", IBrowserPresentation,
                    AbsoluteURL)
        provideView(IRootFolder, "absolute_url", IBrowserPresentation,
                    SiteAbsoluteURL)


    def tearDown(self):
        # clean up folders and placeful service managers and services too?
        CA.getServiceManager_hook = self.__old_getServiceManager_hook
        PlacelessSetup.tearDown(self)

    def buildFolders(self):
        # set up a reasonably complex folder structure
        #
        #     ____________ rootFolder ____________
        #    /                                    \
        # folder1 __________________            folder2
        #   |                       \             |
        # folder1_1 ____           folder1_2    folder2_1
        #   |           \            |            |
        # folder1_1_1 folder1_1_2  folder1_2_1  folder2_1_1
        from zope.app.content.folder import Folder
        from zope.app.content.folder import RootFolder
        from zope.proxy.context import ContextWrapper
        # top
        self.rootFolder = RootFolder()
        # level 1
        self.folder1 = Folder()
        self.rootFolder.setObject("folder1", self.folder1)
        self.folder1 = ContextWrapper(self.folder1, self.rootFolder,
             name = "folder1")
        self.folder2 = Folder()
        self.rootFolder.setObject("folder2", self.folder2)
        self.folder2 = ContextWrapper(self.folder2, self.rootFolder,
             name = "folder2")
        # level 2
        self.folder1_1 = Folder()
        self.folder1.setObject("folder1_1", self.folder1_1)
        self.folder1_1 = ContextWrapper(self.folder1_1, self.folder1,
             name = "folder1_1")
        self.folder1_2 = Folder()
        self.folder1.setObject("folder1_2", self.folder1_2)
        self.folder1_2 = ContextWrapper(self.folder1_2, self.folder1,
             name = "folder1_2")
        self.folder2_1 = Folder()
        self.folder2.setObject("folder2_1", self.folder2_1)
        self.folder2_1 = ContextWrapper(self.folder2_1, self.folder2,
             name = "folder2_1")
        # level 3
        self.folder1_1_1 = Folder()
        self.folder1_1.setObject("folder1_1_1", self.folder1_1_1)
        self.folder1_1_1 = ContextWrapper(self.folder1_1_1, self.folder1_1,
             name = "folder1_1_1")
        self.folder1_1_2 = Folder()
        self.folder1_1.setObject("folder1_1_2", self.folder1_1_2)
        self.folder1_1_2 = ContextWrapper(self.folder1_1_2, self.folder1_1,
             name = "folder1_1_2")
        self.folder1_2_1 = Folder()
        self.folder1_2.setObject("folder1_2_1", self.folder1_2_1)
        self.folder1_2_1 = ContextWrapper(self.folder1_2_1, self.folder1_2,
             name = "folder1_2_1")
        self.folder2_1_1 = Folder()
        self.folder2_1.setObject("folder2_1_1", self.folder2_1_1)
        self.folder2_1_1 = ContextWrapper(self.folder2_1_1, self.folder2_1,
             name = "folder2_1_1")

    def createServiceManager(self, folder = None):
        if folder is None:
            folder = self.rootFolder
        from zope.app.services.tests.servicemanager \
             import TestingServiceManager

        folder.setServiceManager(TestingServiceManager())
