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

$Id: bootstrap.py,v 1.3 2003/07/02 10:59:18 alga Exp $
"""
from transaction import get_transaction
from zope.interface import implements
from zope.app.interfaces.event import ISubscriber
from zope.app.traversing import traverse, traverseName
from zope.app.publication.zopepublication import ZopePublication
from zope.app.content.folder import RootFolder
from zope.app.services.servicenames import HubIds, PrincipalAnnotation
from zope.app.services.servicenames import EventPublication, EventSubscription
from zope.app.services.servicenames import ErrorLogging, Interfaces
from zope.app.services.service import ServiceManager
from zope.app.services.service import ServiceRegistration
from zope.app.services.hub import ObjectHub
from zope.app.services.event import EventService
from zope.app.services.error import ErrorReportingService
from zope.app.services.principalannotation import PrincipalAnnotationService
from zope.app.services.interface import LocalInterfaceService
from zope.proxy import removeAllProxies
from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.event import function
from zope.component.exceptions import ComponentLookupError

class BootstrapSubscriberBase:
    """A startup event subscriber base class.

    Ensures the root folder and the service manager are created.
    Subclasses may create local services by overriding the doSetup()
    method.
    """

    implements(ISubscriber)

    def doSetup(self):
        """Instantiate some service.

        This method is meant to be overriden in the subclasses.
        """
        pass

    def notify(self, event):

        db = event.database
        connection = db.open()
        root = connection.root()
        self.root_folder = root.get(ZopePublication.root_name, None)
        self.root_created = False

        if self.root_folder is None:
            self.root_created = True
            self.root_folder = RootFolder()
            root[ZopePublication.root_name] = self.root_folder

        try:
            self.service_manager = traverse(self.root_folder, '/++etc++site')
        except ComponentLookupError:
            self.service_manager = ServiceManager()
            self.root_folder.setServiceManager(self.service_manager)

        self.doSetup()

        get_transaction().commit()
        connection.close()

    def ensureService(self, service_type, service_factory, **kw):
        """Add and configure a service to the root folder if it's
        not yet provided.

        Returns the name added or None if nothing was added.
        """
        if not self.service_manager.queryLocalService(service_type):
            return addConfigureService(self.root_folder, service_type,
                                       service_factory, **kw)
        else:
            return None

class BootstrapInstance(BootstrapSubscriberBase):
    """Bootstrap a Zope3 instance given a database object.

    This first checks if the root folder exists and has a service
    manager.  If it exists, nothing else is changed.  If no root
    folder exists, one is added, and several essential services are
    added and configured.
    """

    def doSetup(self):
        """Add essential services.

        XXX This ought to be configurable.  For now, hardcode some
        services we know we all need.
        """

        # The EventService class implements two services
        name = self.ensureService(EventPublication, EventService)
        if name:
            configureService(self.root_folder, EventSubscription, name)

        # Add the HubIds service, which subscribes itself to the event service
        name = self.ensureService(HubIds, ObjectHub)

        # Sundry other services
        self.ensureService(ErrorLogging,
                           ErrorReportingService, copy_to_zlog=True)
        self.ensureService(PrincipalAnnotation, PrincipalAnnotationService)

bootstrapInstance = BootstrapInstance()

class CreateInterfaceService(BootstrapSubscriberBase):
    """A subscriber to the startup event which ensures that a local
    interface service is available.
    """

    def doSetup(self):
        if not self.service_manager.queryLocalService(Interfaces):
            addConfigureService(self.root_folder, Interfaces, LocalInterfaceService)

createInterfaceService = CreateInterfaceService()


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
    # registration; hence all the traverse() and traverseName() calls.
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

def configureService(root_folder, service_type, name, initial_status='Active'):
    """Configure a service in the root folder."""
    package_name = '/++etc++site/default'
    package = traverse(root_folder, package_name)
    registration_manager = package.getRegistrationManager()
    registration =  ServiceRegistration(service_type,
                                        name,
                                        registration_manager)
    key = registration_manager.setObject("", registration)
    registration = traverseName(registration_manager, key)
    registration.status = initial_status
