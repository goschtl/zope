##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Bootstrap code.

This module contains code to bootstrap a Zope3 instance.  For example
it makes sure a root folder exists and creates and configures some
essential services.

$Id: bootstrap.py,v 1.15 2003/04/12 11:52:18 stevea Exp $
"""
from transaction import get_transaction

from zope.app.traversing import traverse, traverseName
from zope.app.publication.zopepublication import ZopePublication
from zope.app.content.folder import RootFolder
from zope.app.services.servicenames import EventPublication, HubIds, EventSubscription
from zope.app.services.servicenames import ErrorLogging
from zope.app.services.service import ServiceManager
from zope.app.services.service import ServiceConfiguration
from zope.app.services.hub import ObjectHub
from zope.app.services.event import EventService
from zope.app.services.errorr import ErrorReportingService
from zope.app.services.principalannotation import PrincipalAnnotationService
from zope.app.container.zopecontainer import ZopeContainerAdapter
from zope.proxy.introspection import removeAllProxies
from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent

def bootstrapInstance(db):
    """Bootstrap a Zope3 instance given a database object.

    This first checks if the root folder exists.  If it exists, nothing
    is changed.  If no root folder exists, one is added, and several
    essential services are added and configured.
    """
    connection = db.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, None)

    if root_folder is None:
        # Bootstrap code

        root_folder = RootFolder()
        addEssentialServices(root_folder)
        root[ZopePublication.root_name] = root_folder

        publish(root_folder, ObjectCreatedEvent(root_folder))
        get_transaction().commit()

    connection.close()


def addEssentialServices(root_folder):
    """Add essential services.

    XXX This ought to be configurable.  For now, hardcode some
    services we know we all need.
    """
    service_manager = ServiceManager()
    root_folder.setServiceManager(service_manager)

    # The EventService class implements two services
    name = addConfigureService(root_folder, EventPublication, EventService)
    configureService(root_folder, EventSubscription, name)

    # Add the HubIds service, which subscribes itself to the event service
    name = addService(root_folder, HubIds, ObjectHub)
    configureService(root_folder, HubIds, name)

    # Sundry other services
    addConfigureService(root_folder, ErrorLogging,
                        ErrorReportingService, copy_to_zlog=True)
    addConfigureService(root_folder, 'PrincipalAnnotation',
                        PrincipalAnnotationService)


def addConfigureService(root_folder, service_type, service_factory, **kw):
    """Add and configure a service to the root folder."""
    name = addService(root_folder, service_type, service_factory, **kw)
    configureService(root_folder, service_type, name)
    return name

def addService(root_folder, service_type, service_factory, **kw):
    """Add a service to the root folder.

    The service is added to the default package and activated.
    This assumes the root folder already has a service manager,
    and that we add at most one service of each type.

    Returns the name of the service implementation in the default package.
    """
    # The code here is complicated by the fact that the registry
    # calls at the end require a fully context-wrapped
    # configuration; hence all the traverse() and traverseName() calls.
    package_name = '/++etc++site/default'
    package = traverse(root_folder, package_name)
    name = service_type + '-1'
    service = service_factory()
    service = removeAllProxies(service)
    package.setObject(name, service)

    # Set additional attributes on the service
    for k, v in kw.iteritems():
        setattr(service, k, v)
    return name

def configureService(root_folder, service_type, name,
                     initial_status='Active'):
    """Configure a service in the root folder."""
    package_name = '/++etc++site/default'
    package = traverse(root_folder, package_name)
    configuration_manager = package.getConfigurationManager()
    configuration =  ServiceConfiguration(service_type,
                                          package_name + '/' + name,
                                          root_folder)
    cm = ZopeContainerAdapter(configuration_manager)
    key = cm.setObject("", configuration)
    configuration = traverseName(configuration_manager, key)
    configuration.status = initial_status
