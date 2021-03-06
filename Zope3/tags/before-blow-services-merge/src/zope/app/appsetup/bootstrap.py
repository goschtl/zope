##############################################################################
#
# Copyright (c) 2002, 2004 Zope Corporation and Contributors.
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
__docformat__ = 'restructuredtext'

from transaction import get_transaction
from zope.app.publication.zopepublication import ZopePublication
from zope.interface import implements
from zope.app.traversing.interfaces import TraversalError

from zope.app import zapi
from zope.app.traversing.api import traverse, traverseName
from zope.app.publication.zopepublication import ZopePublication
from zope.app.folder import rootFolder
from zope.app.servicenames import Utilities
from zope.app.site.service import ServiceManager, ServiceRegistration
from zope.app.container.interfaces import INameChooser
from zope.app.utility import UtilityRegistration, LocalUtilityService
from zope.app.utility.interfaces import ILocalUtilityService

def ensureObject(root_folder, object_name, object_type, object_factory):
    """Check that there's a basic object in the service
    manager. If not, add one.

    Return the name abdded, if we added an object, otherwise None.
    """
    package = getServiceManagerDefault(root_folder)
    valid_objects = [ name
                      for name in package
                      if object_type.providedBy(package[name]) ]
    if valid_objects:
        return None
    name = object_name
    obj = object_factory()
    package[name] = obj
    return name

def ensureService(service_manager, root_folder, service_type,
                  service_factory, **kw):
    """Add and configure a service to the root folder if it's
    not yet provided.

    Returns the name added or None if nothing was added.
    """
    if not service_manager.queryLocalService(service_type):
        # The site-manager may have chosen to disable one of the
        # core services. Their loss. The alternative is that when
        # they restart, they get a new service of the one that
        # they chose to disable.
        reg = service_manager.queryRegistrations(service_type)
        if reg is None:
            return addConfigureService(root_folder, service_type,
                                       service_factory, **kw)
    else:
        return None

def ensureUtility(root_folder, interface, utility_type,
                  utility_factory, name='', **kw):
    """Add a utility to the top Utility Service

    Returns the name added or ``None`` if nothing was added.
    """
    utility_manager = zapi.getService(Utilities, root_folder)
    utils = list(utility_manager.getLocalUtilitiesFor(interface))
    if len(utils) == 0:
        return addConfigureUtility(
            root_folder, interface, utility_type, utility_factory,
            name, **kw
            )
    else:
        return None

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

def configureService(root_folder, service_type, name, initial_status=u'Active'):
    """Configure a service in the root folder."""
    package = getServiceManagerDefault(root_folder)
    registration_manager = package.getRegistrationManager()
    registration =  ServiceRegistration(service_type,
                                        package[name],
                                        registration_manager)
    key = registration_manager.addRegistration(registration)
    registration = traverseName(registration_manager, key)
    registration.status = initial_status

def addConfigureUtility(
        root_folder, interface, utility_type, utility_factory, name='', **kw):
    """Add and configure a service to the root folder."""
    utility_name = addUtility(root_folder, utility_type, utility_factory, **kw)
    configureUtility(root_folder, interface, utility_type, name, utility_name)
    return name

def addUtility(root_folder, utility_type, utility_factory, **kw):
    """ Add a Utility to the root folder's Utility Service.

    The utility is added to the default package and activated.
    This assumes that the root folder already has a Utility Service.
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
        initial_status=u'Active'):
    """Configure a utility in the root folder."""
    package = getServiceManagerDefault(root_folder)
    registration_manager = package.getRegistrationManager()
    registration = UtilityRegistration(name, interface, package[folder_name])
    key = registration_manager.addRegistration(registration)
    registration.status = initial_status

def getServiceManagerDefault(root_folder):
    package_name = '/++etc++site/default'
    package = traverse(root_folder, package_name)
    return package

def getInformationFromEvent(event):
    """ Extracts information from the event

    Return a tuple containing

      - db
      - connection open from the db
      - root connection object
      - the root_folder object
    """
    db = event.database
    connection = db.open()
    root = connection.root()
    root_folder = root.get(ZopePublication.root_name, None)
    return db, connection, root, root_folder

def getServiceManager(root_folder):
    """ Returns the Service Manager from the root_folder object
    """
    try:
        service_manager = traverse(root_folder, '++etc++site')
    except TraversalError:
        service_manager = ServiceManager(root_folder)
        root_folder.setSiteManager(service_manager)
    return service_manager

######################################################################
######################################################################

def bootStrapSubscriber(event):
    """The actual subscriber to the bootstrap IDataBaseOpenedEvent

    Boostrap a Zope3 instance given a database object This first checks if the
    root folder exists and has a service manager.  If it exists, nothing else
    is changed.  If no root folder exists, one is added, and several essential
    services are added and configured.
    """

    db, connection, root, root_folder = getInformationFromEvent(event)
    root_created = False

    if root_folder is None:
        root_created = True
        # ugh... we depend on the root folder implementation
        root_folder = rootFolder()
        root[ZopePublication.root_name] = root_folder
        service_manager = getServiceManager(root_folder)

        # Sundry other services
        ensureService(service_manager, root_folder, Utilities,
                      LocalUtilityService)

        get_transaction().commit()
        connection.close()

########################################################################
########################################################################
