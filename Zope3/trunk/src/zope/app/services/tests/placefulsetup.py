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
$Id: placefulsetup.py,v 1.8 2003/02/12 02:17:34 seanb Exp $
"""
from zope import component as CA
from zope.component.adapter import provideAdapter
from zope.component.view import provideView
from zope.app.services.servicenames import HubIds, Events, Subscription
from zope.publisher.interfaces.browser import IBrowserPresentation

from zope.app.browser.absoluteurl import SiteAbsoluteURL, AbsoluteURL
from zope.app.component import hooks
from zope.app.container.traversal import ContainerTraversable
from zope.app.interfaces.container import ISimpleReadContainer
from zope.app.interfaces.content.folder import IRootFolder
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.interfaces.traversing import IPhysicallyLocatable
from zope.app.interfaces.traversing import ITraverser, ITraversable
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.traversing.namespace import etc, provideNamespaceHandler
from zope.app.traversing.adapters import DefaultTraversable
from zope.app.traversing.adapters import WrapperPhysicallyLocatable
from zope.app.traversing.adapters import Traverser, RootPhysicallyLocatable
from zope.app.traversing import traverse, getPhysicalPathString
from zope.app.services.service import ServiceManager, ServiceConfiguration
from zope.app.interfaces.services.configuration import Active

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
        from zope.proxy.context import ContextWrapper
        # top
        self.createRootFolder()
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

    def createServiceManager(self, folder=None):
        if folder is None:
            folder = self.rootFolder
        from zope.app.services.tests.servicemanager \
             import TestingServiceManager
        folder.setServiceManager(TestingServiceManager())

    def createRootFolder(self):
        from zope.app.content.folder import RootFolder
        self.rootFolder = RootFolder()

    def getObjectHub(self):
        from zope.app.services.hub import ObjectHub
        return ObjectHub()

    def createEventService(self, folder_path):
        """Create an event service in 'folder', and configure it for
        Events and Subscription services."""
        folder = traverse(self.rootFolder, folder_path)
        if not folder.hasServiceManager():
            folder.setServiceManager(ServiceManager())
        sm = traverse(folder, '++etc++Services')
        default = traverse(sm, 'Packages/default')
        service_name = 'anEventService'
        from zope.app.services.event import EventService
        default.setObject(service_name, EventService())

        path = "%s/%s" % (getPhysicalPathString(default), service_name)
        configuration = ServiceConfiguration(Events, path)
        default['configure'].setObject(
                "%sEventsDir" % service_name, configuration)
        traverse(default, 'configure/1').status = Active

        configuration = ServiceConfiguration(Subscription, path)
        default['configure'].setObject(
                "%sSubscriptionServiceDir" % service_name, configuration)
        traverse(default, 'configure/2').status = Active

    def createStandardServices(self):
        '''Create a bunch of standard placeful services'''
        if not hasattr(self, 'rootFolder'):
            self.createRootFolder()
        root = self.rootFolder
        if root.hasServiceManager():
            raise RuntimeError('ServiceManager already exists, so cannot '
                               'create standard services')
        root.setServiceManager(ServiceManager())
        from zope.component import getServiceManager        
        defineService = getServiceManager(None).defineService

        from zope.app.interfaces.services.hub import IObjectHub
        from zope.app.interfaces.services.event import ISubscriptionService
        from zope.app.services.event import EventService
        defineService(Subscription, ISubscriptionService)

        # Events service already defined by
        # zope.app.events.tests.PlacelessSetup

        defineService(HubIds, IObjectHub)

        sm = traverse(root, '++etc++Services')
        default = traverse(sm, 'Packages/default')
        default.setObject("myEventService", EventService())
        default.setObject("myObjectHub", self.getObjectHub())

        path = "%s/Packages/default/myEventService" % getPhysicalPathString(sm)
        configuration = ServiceConfiguration(Events, path)
        default['configure'].setObject("myEventServiceDir", configuration)
        traverse(default, 'configure/1').status = Active

        configuration = ServiceConfiguration(Subscription, path)
        default['configure'].setObject(
                "mySubscriptionServiceDir", configuration)
        traverse(default, 'configure/2').status = Active

        path = "%s/Packages/default/myObjectHub" % getPhysicalPathString(sm)
        configuration = ServiceConfiguration(HubIds, path)
        default['configure'].setObject("myHubIdsServiceDir", configuration)
        traverse(default, 'configure/3').status = Active

