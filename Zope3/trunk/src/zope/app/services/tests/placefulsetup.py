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
$Id: placefulsetup.py,v 1.20 2003/05/18 18:06:43 jim Exp $
"""
from zope.app.attributeannotations import AttributeAnnotations
from zope.app.browser.absoluteurl import SiteAbsoluteURL, AbsoluteURL
from zope.app.component import hooks
from zope.app.container.traversal import ContainerTraversable
from zope.app.dependable import Dependable
from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.container import ISimpleReadContainer
from zope.app.interfaces.dependable import IDependable
from zope.app.interfaces.services.configuration import Active
from zope.app.interfaces.services.configuration import IAttributeUseConfigurable
from zope.app.interfaces.services.configuration import IUseConfiguration
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.interfaces.traversing import IPhysicallyLocatable
from zope.app.interfaces.traversing import ITraverser, ITraversable
from zope.app.services.configuration import UseConfiguration
from zope.app.services.service import ServiceManager, ServiceConfiguration
from zope.app.services.servicenames import EventPublication, EventSubscription
from zope.app.services.servicenames import HubIds
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.traversing.adapters import DefaultTraversable
from zope.app.traversing.adapters import Traverser, RootPhysicallyLocatable
from zope.app.traversing.adapters import WrapperPhysicallyLocatable
from zope.app.traversing import traverse, getPath
from zope.app.traversing.namespace import etc, provideNamespaceHandler
from zope.component.adapter import provideAdapter
from zope.component.view import provideView
from zope import component as CA
from zope.publisher.interfaces.browser import IBrowserPresentation

class PlacefulSetup(PlacelessSetup):

    def setUp(self):
        PlacelessSetup.setUp(self)
        # set up placeful hooks, saving originals for tearDown
        CA.getServiceManager.sethook(hooks.getServiceManager_hook)
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

        provideAdapter(IAttributeUseConfigurable, IUseConfiguration,
                       UseConfiguration)
        provideAdapter(IAttributeAnnotatable, IAnnotations,
                       AttributeAnnotations)

        provideAdapter(IAttributeAnnotatable, IDependable, Dependable)

        # set up etc namespace
        provideNamespaceHandler("etc", etc)

        provideView(None, "absolute_url", IBrowserPresentation,
                    AbsoluteURL)
        provideView(IContainmentRoot, "absolute_url", IBrowserPresentation,
                    SiteAbsoluteURL)


    def tearDown(self):
        # clean up folders and placeful service managers and services too?
        CA.getServiceManager.reset()
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
        EventPublication and EventSubscription services."""
        folder = traverse(self.rootFolder, folder_path)
        if not folder.hasServiceManager():
            folder.setServiceManager(ServiceManager())
        sm = traverse(folder, '++etc++site')
        default = traverse(sm, 'default')
        service_name = 'anEventService'
        from zope.app.services.event import EventService
        default.setObject(service_name, EventService())

        path = "%s/%s" % (getPath(default), service_name)
        configuration = ServiceConfiguration(EventPublication, path, self.rootFolder)
        default.getConfigurationManager().setObject(
                "%sEventsDir" % service_name, configuration)
        traverse(default.getConfigurationManager(), '1').status = Active

        configuration = ServiceConfiguration(EventSubscription, path,
                                             self.rootFolder)
        default.getConfigurationManager().setObject(
                "%sSubscriptionServiceDir" % service_name, configuration)
        traverse(default.getConfigurationManager(), '2').status = Active

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
        defineService(EventSubscription, ISubscriptionService)

        # EventPublication service already defined by
        # zope.app.events.tests.PlacelessSetup

        defineService(HubIds, IObjectHub)

        sm = traverse(root, '++etc++site')
        default = traverse(sm, 'default')
        default.setObject("myEventService", EventService())
        default.setObject("myObjectHub", self.getObjectHub())

        path = "%s/default/myEventService" % getPath(sm)
        configuration = ServiceConfiguration(EventPublication, path,
                                             self.rootFolder)
        default.getConfigurationManager().setObject(
            "myEventServiceDir", configuration)
        traverse(default.getConfigurationManager(), '1').status = Active

        configuration = ServiceConfiguration(EventSubscription, path,
                                             self.rootFolder)
        default.getConfigurationManager().setObject(
                "mySubscriptionServiceDir", configuration)
        traverse(default.getConfigurationManager(), '2').status = Active

        path = "%s/default/myObjectHub" % getPath(sm)
        configuration = ServiceConfiguration(HubIds, path, self.rootFolder)
        default.getConfigurationManager().setObject("myHubIdsServiceDir",
                                                    configuration)
        traverse(default.getConfigurationManager(), '3').status = Active

def addService(servicemanager, name, service):
    default = traverse(servicemanager, 'default')
    default.setObject(name, service)
    path = "%s/default/%s" % (getPath(servicemanager), name)
    configuration = ServiceConfiguration(name, path, servicemanager)
    default.getConfigurationManager().setObject("", configuration)
    traverse(default.getConfigurationManager(), '1').status = Active
    

def createServiceManager(folder):
    folder.setServiceManager(ServiceManager())
    return traverse(folder, "++etc++site")
