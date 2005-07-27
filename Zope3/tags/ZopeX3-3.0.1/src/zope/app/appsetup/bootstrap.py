##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Bootstrap code.

This module contains code to bootstrap a Zope3 instance.  For example
it makes sure a root folder exists and creates and configures some
essential services.

$Id$
"""
import transaction
from zope.app.publication.zopepublication import ZopePublication
from zope.interface import implements
from zope.component.exceptions import ComponentLookupError

from zope.app import zapi
from zope.app.traversing.api import traverse, traverseName
from zope.app.publication.zopepublication import ZopePublication
from zope.app.folder import rootFolder
from zope.app.servicenames import PrincipalAnnotation
from zope.app.servicenames import ErrorLogging, Utilities
from zope.app.site.service import ServiceManager, ServiceRegistration
from zope.app.errorservice import RootErrorReportingService
from zope.app.container.interfaces import INameChooser
from zope.app.utility import UtilityRegistration, LocalUtilityService

# XXX It should be possible to remove each of these from the basic
# bootstrap, at which point we can remove the
# zope.app.principalannotation packages from
# zope.app.

from zope.app.principalannotation import PrincipalAnnotationService


class BootstrapSubscriberBase(object):
    """A startup event subscriber base class.

    Ensures the root folder and the service manager are created.
    Subclasses may create local services by overriding the doSetup()
    method.
    """

    def doSetup(self):
        """Instantiate some service.

        This method is meant to be overriden in the subclasses.
        """
        pass

    def __call__(self, event):

        db = event.database
        connection = db.open()
        root = connection.root()
        self.root_folder = root.get(ZopePublication.root_name, None)
        self.root_created = False

        if self.root_folder is None:
            self.root_created = True
            # ugh... we depend on the root folder implementation
            self.root_folder = rootFolder()
            root[ZopePublication.root_name] = self.root_folder

        try:
            self.service_manager = traverse(self.root_folder, '++etc++site')
        except ComponentLookupError:
            self.service_manager = ServiceManager(self.root_folder)
            self.root_folder.setSiteManager(self.service_manager)

        self.doSetup()

        transaction.commit()
        connection.close()

    def ensureObject(self, object_name, object_type, object_factory):
        """Check that there's a basic object in the service
        manager. If not, add one.

        Return the name added, if we added an object, otherwise None.
        """
        package = getServiceManagerDefault(self.root_folder)
        valid_objects = [ name
                          for name in package
                          if object_type.providedBy(package[name]) ]
        if valid_objects:
            return None
        name = object_name
        obj = object_factory()
        package[name] = obj
        return name

    def ensureService(self, service_type, service_factory, **kw):
        """Add and configure a service to the root folder if it's
        not yet provided.

        Returns the name added or None if nothing was added.
        """
        if not self.service_manager.queryLocalService(service_type):
            # The site-manager may have chosen to disable one of the
            # core services. Their loss. The alternative is that when
            # they restart, they get a new service of the one that 
            # they chose to disable. 
            reg = self.service_manager.queryRegistrations(service_type)
            if reg is None:
                return addConfigureService(self.root_folder, service_type,
                                           service_factory, **kw)
        else:
            return None

    def ensureUtility(
            self, interface, utility_type, utility_factory, name='', **kw):
        """Add a utility to the top Utility Service
        
        Returns the name added or None if nothing was added.
        """
        utility_manager = zapi.getService(Utilities, self.root_folder)
        utility = utility_manager.queryUtility(interface, name)
        if utility is None:
            return addConfigureUtility(
                    self.root_folder, interface, utility_type, utility_factory,
                    name, **kw
                    )
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

        # Sundry other services
        self.ensureService(ErrorLogging,
                           RootErrorReportingService, copy_to_zlog=True)
        self.ensureService(PrincipalAnnotation, PrincipalAnnotationService)

        self.ensureService(Utilities, LocalUtilityService)

bootstrapInstance = BootstrapInstance()


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
    package = getServiceManagerDefault(root_folder)
    chooser = INameChooser(package)
    service = service_factory()
    name = chooser.chooseName(service_type, service)
    package[name] = service

    # Set additional attributes on the service
    for k, v in kw.iteritems():
        setattr(service, k, v)
    return name

def configureService(root_folder, service_type, name, initial_status='Active'):
    """Configure a service in the root folder."""
    package = getServiceManagerDefault(root_folder)
    registration_manager = package.getRegistrationManager()
    registration =  ServiceRegistration(service_type,
                                        name,
                                        registration_manager)
    key = registration_manager.addRegistration(registration)
    registration = traverseName(registration_manager, key)
    registration.status = initial_status

def addConfigureUtility(
        root_folder, interface, utility_type, utility_factory, name='', **kw):
    """Add and configure a service to the root folder."""
    folder_name = addUtility(root_folder, utility_type, utility_factory, **kw)
    configureUtility(root_folder, interface, utility_type, name, folder_name)
    return name

def addUtility(root_folder, utility_type, utility_factory, **kw):
    """ Add a Utility to the root folders Utility Service.

    The utility is added to the default package and activated.
    This assumes the root folder already as a Utility Service
    """
    package = getServiceManagerDefault(root_folder)
    chooser = INameChooser(package)
    utility = utility_factory()
    name = chooser.chooseName(utility_type, utility)
    package[name] = utility
    # Set additional attributes on the utility
    for k, v in kw.iteritems():
        setattr(utility, k, v)
    return name

def configureUtility(
        root_folder, interface, utility_type, name, folder_name,
        initial_status='Active'):
    """Configure a utility in the root folder."""
    package = getServiceManagerDefault(root_folder)
    registration_manager = package.getRegistrationManager()
    registration = UtilityRegistration(name, interface, folder_name)
    key = registration_manager.addRegistration(registration)
    registration.status = initial_status

def getServiceManagerDefault(root_folder):
    package_name = '/++etc++site/default'
    package = traverse(root_folder, package_name)
    return package
