##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Setting up an environment for testing context-dependent objects

$Id: setup.py,v 1.6 2003/09/02 20:46:51 jim Exp $
"""

import zope.component
from zope.app import zapi
from zope.component.adapter import provideAdapter
from zope.component.view import provideView
from zope.interface import classImplements

#------------------------------------------------------------------------
# Annotations
from zope.app.attributeannotations import AttributeAnnotations
from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.annotation import IAttributeAnnotatable
def setUpAnnotations():
    provideAdapter(IAttributeAnnotatable, IAnnotations,
                   AttributeAnnotations)

#------------------------------------------------------------------------
# Dependencies
from zope.app.dependable import Dependable
from zope.app.interfaces.dependable import IDependable
def setUpDependable():
    provideAdapter(IAttributeAnnotatable, IDependable,
                   Dependable)

#------------------------------------------------------------------------
# Traversal
from zope.app.browser.absoluteurl import SiteAbsoluteURL, AbsoluteURL
from zope.app.container.traversal import ContainerTraversable
from zope.app.interfaces.container import ISimpleReadContainer
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.interfaces.traversing import IPhysicallyLocatable
from zope.app.interfaces.traversing import ITraverser, ITraversable
from zope.app.traversing.adapters import DefaultTraversable
from zope.app.traversing.adapters import Traverser, RootPhysicallyLocatable
from zope.app.traversing.adapters import WrapperPhysicallyLocatable
from zope.app.traversing.namespace import etc, provideNamespaceHandler
from zope.publisher.interfaces.browser import IBrowserPresentation
def setUpTraversal():
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
    provideView(IContainmentRoot, "absolute_url", IBrowserPresentation,
                SiteAbsoluteURL)

#------------------------------------------------------------------------
# Use registration
from zope.app.interfaces.services.registration import IAttributeRegisterable
from zope.app.interfaces.services.registration import IRegistered
from zope.app.services.registration import Registered
def setUpRegistered():
    provideAdapter(IAttributeRegisterable, IRegistered,
                   Registered)


#------------------------------------------------------------------------
# Placeful setup
from zope.app.component.hooks import getServiceManager_hook
from zope.app.tests.placelesssetup import setUp as placelessSetUp
from zope.app.tests.placelesssetup import tearDown as placelessTearDown
def placefulSetUp(site=False):
    placelessSetUp()
    zope.component.getServiceManager.sethook(getServiceManager_hook)
    setUpAnnotations()
    setUpDependable()
    setUpTraversal()
    setUpRegistered()

    if site:
        site = RootFolder()
        createServiceManager(site)
        return site

def placefulTearDown():
    placelessTearDown()
    zope.component.getServiceManager.reset()


from zope.app.content.folder import Folder, RootFolder
def buildSampleFolderTree():
    # set up a reasonably complex folder structure
    #
    #     ____________ rootFolder ____________
    #    /                                    \
    # folder1 __________________            folder2
    #   |                       \             |
    # folder1_1 ____           folder1_2    folder2_1
    #   |           \            |            |
    # folder1_1_1 folder1_1_2  folder1_2_1  folder2_1_1

    root = RootFolder()
    root.setObject('folder1', Folder())
    root['folder1'].setObject('folder1_1', Folder())
    root['folder1']['folder1_1'].setObject('folder1_1_1', Folder())
    root['folder1']['folder1_1'].setObject('folder1_1_2', Folder())
    root['folder1'].setObject('folder1_2', Folder())
    root['folder1']['folder1_2'].setObject('folder1_2_1', Folder())
    root.setObject('folder2', Folder())
    root['folder2'].setObject('folder2_1', Folder())
    root['folder2']['folder2_1'].setObject('folder2_1_1', Folder())

    return root


from zope.app.services.service import ServiceManager
from zope.app.interfaces.services.service import ISite
def createServiceManager(folder):
    if not ISite.isImplementedBy(folder):
        folder.setSiteManager(ServiceManager())

    return zapi.traverse(folder, "++etc++site")

from zope.app.services.service import ServiceRegistration
from zope.app.interfaces.services.registration import ActiveStatus
def addService(servicemanager, name, service, suffix=''):
    """Add a service to a service manager

    This utility is useful for tests that need to set up services.
    """
    default = zapi.traverse(servicemanager, 'default')
    default.setObject(name+suffix, service)
    path = "%s/default/%s" % (zapi.getPath(servicemanager), name+suffix)
    registration = ServiceRegistration(name, path, servicemanager)
    key = default.getRegistrationManager().setObject("", registration)
    zapi.traverse(default.getRegistrationManager(), key).status = ActiveStatus
    return zapi.traverse(servicemanager, path)


from zope.component import getServiceManager
from zope.app.interfaces.services.hub import IObjectHub
from zope.app.interfaces.services.event import ISubscriptionService
from zope.app.services.event import EventService
from zope.app.services.hub import ObjectHub
from zope.app.services.servicenames import HubIds
from zope.app.services.servicenames import EventPublication, EventSubscription
def createStandardServices(folder, hubids=None):
    '''Create a bunch of standard placeful services

    Well, uh, 3
    '''
    sm = createServiceManager(folder)
    defineService = getServiceManager(None).defineService

    defineService(EventSubscription, ISubscriptionService)

    # EventPublication service already defined by
    # zope.app.events.tests.PlacelessSetup

    defineService(HubIds, IObjectHub)

    # EventService must be IAttributeAnnotatable so that it can support
    # dependencies.
    classImplements(EventService, IAttributeAnnotatable)
    events = EventService()
    addService(sm, EventPublication, events)
    addService(sm, EventSubscription, events, suffix='sub')
    if hubids is None:
        hubids = ObjectHub()

    addService(sm, HubIds, hubids)
