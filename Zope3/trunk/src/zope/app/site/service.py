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
"""Service manager implementation

A service manager has a number of roles:

  - A service service

  - A place to do TTW development or to manage database-based code

  - A registry for persistent modules.  The Zope import hook uses the
    ServiceManager to search for modules.  (This functionality will
    eventually be replaced by a separate module service.)

$Id: service.py,v 1.1 2004/03/13 15:21:47 srichter Exp $
"""
from transaction import get_transaction
from zodbcode.module import PersistentModuleRegistry
from zope.app.component.nextservice import getNextService
from zope.app.component.nextservice import getNextServiceManager
from zope.app.container.btree import BTreeContainer
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.contained import Contained
from zope.app.container.interfaces import IContainer
from zope.app.event.function import Subscriber
from zope.app import zapi
from interfaces import IBindingAware, ILocalService, IServiceRegistration
from interfaces import IPossibleSite, ISite, ISiteManager
from zope.app.interfaces.services.registration import IRegistry
from zope.app.interfaces.traversing import IContainmentRoot
from zope.app.location import inside
from zope.app.site.folder import SiteManagementFolder
from zope.app.services.registration import ComponentRegistration
from zope.app.services.registration import RegistrationStack
from zope.app.traversing import getPath
from zope.component.exceptions import ComponentLookupError
from zope.component import getServiceManager
from zope.fssync.server.entryadapter import AttrMapping, DirectoryAdapter
from zope.proxy import removeAllProxies
import sys
import zope.app.interfaces.services.registration
import zope.interface


class IRegistrationManagerContainerContainer(zope.interface.Interface):

    def __setitem__(name, folder):
        """Add a site-management folder
        """
    __setitem__.precondition = ItemTypePrecondition(
       zope.app.interfaces.services.registration.IRegistrationManagerContainer)


class SiteManager(
    BTreeContainer,
    PersistentModuleRegistry,
    ):

    zope.interface.implements(
        ISiteManager,
        IRegistrationManagerContainerContainer,
        IRegistry,
        )

    def __init__(self, site):
        self._bindings = {}
        self.__parent__ = site
        self.__name__ = '++etc++site'
        BTreeContainer.__init__(self)
        PersistentModuleRegistry.__init__(self)
        self.subSites = ()
        self._setNext(site)
        self['default'] = SiteManagementFolder()

    def _setNext(self, site):
        """Find set the next service manager
        """
        while True:
            if IContainmentRoot.providedBy(site):
                # we're the root site, use the global sm
                self.next = zapi.getServiceManager(None)
                return
            site = site.__parent__
            if site is None:
                raise TypeError("Not enough context information")
            if ISite.providedBy(site):
                self.next = site.getSiteManager()
                self.next.addSubsite(self)
                return

    def addSubsite(self, sub):
        """See ISiteManager interface
        """
        subsite = sub.__parent__

        # Update any sites that are now in the subsite:
        subsites = []
        for s in self.subSites:
            if inside(s, subsite):
                s.next = sub
                sub.addSubsite(s)
            else:
                subsites.append(s)

        subsites.append(sub)
        self.subSites = tuple(subsites)

    def queryRegistrationsFor(self, cfg, default=None):
        """See IRegistry"""
        return self.queryRegistrations(cfg.name, default)

    def queryRegistrations(self, name, default=None):
        """See INameRegistry"""
        return self._bindings.get(name, default)

    def createRegistrationsFor(self, cfg):
        """See IRegistry"""
        return self.createRegistrations(cfg.name)

    def createRegistrations(self, name):
        try:
            registry = self._bindings[name]
        except KeyError:
            registry = RegistrationStack(self)
            self._bindings[name] = registry
            self._p_changed = 1
        return registry

    def listRegistrationNames(self):
        return filter(self._bindings.get,
                      self._bindings.keys())

    def queryActiveComponent(self, name, default=None):
        registry = self.queryRegistrations(name)
        if registry:
            registration = registry.active()
            if registration is not None:
                return registration.getComponent()
        return default

    def getServiceDefinitions(wrapped_self):
        """See IServiceService
        """
        # Get the services defined here and above us, if any (as held
        # in a ServiceInterfaceService, presumably)
        sm = getNextServiceManager(wrapped_self)
        if sm is not None:
            serviceDefs = sm.getServiceDefinitions()
        else: serviceDefs = {}

        return serviceDefs

    def queryService(wrapped_self, name, default=None):
        """See IServiceService
        """
        try:
            return wrapped_self.getService(name)
        except ComponentLookupError:
            return default

    def getService(wrapped_self, name):
        """See IServiceService
        """

        # This is rather tricky. Normally, getting a service requires
        # the use of other services, like the adapter service.  We
        # need to be careful not to get into an infinate recursion by
        # getting out getService to be called while looking up
        # services, so we'll

        if name == 'Services':
            return wrapped_self # We are the service service

        if not getattr(wrapped_self, '_v_calling', 0):

            wrapped_self._v_calling = 1
            try:
                service = wrapped_self.queryActiveComponent(name)
                if service is not None:
                    return service

            finally:
                wrapped_self._v_calling = 0

        return getNextService(wrapped_self, name)


    def queryLocalService(wrapped_self, name, default=None):
        """See ISiteManager
        """

        # This is rather tricky. Normally, getting a service requires
        # the use of other services, like the adapter service.  We
        # need to be careful not to get into an infinate recursion by
        # getting our getService to be called while looking up
        # services, so we'll use _v_calling to prevent recursive
        # getService calls.

        if name == 'Services':
            return wrapped_self # We are the service service

        if not getattr(wrapped_self, '_v_calling', 0):

            wrapped_self._v_calling = 1
            try:
                service = wrapped_self.queryActiveComponent(name)
                if service is not None:
                    return service

            finally:
                wrapped_self._v_calling = 0

        return default

    def getInterfaceFor(wrapped_self, service_type):
        """See IServiceService
        """
        for type, interface in wrapped_self.getServiceDefinitions():
            if type == service_type:
                return interface

        raise NameError(service_type)

    def queryComponent(self, type=None, filter=None, all=0):
        local = []
        path = getPath(self)
        for pkg_name in self:
            package = self[pkg_name]
            for name in package:
                component = package[name]
                if type is not None and not type.providedBy(component):
                    continue
                if filter is not None and not filter(component):
                    continue
                local.append({'path': "%s/%s/%s" % (path, pkg_name, name),
                              'component': component,
                              })

        if all:
            next_service_manager = getNextServiceManager(self)
            if IComponentManager.providedBy(next_service_manager):
                next_service_manager.queryComponent(type, filter, all)

            local += list(all)

        return local

    def findModule(wrapped_self, name):
        # override to pass call up to next service manager
        mod = super(ServiceManager,
                    removeAllProxies(wrapped_self)).findModule(name)
        if mod is not None:
            return mod

        sm = getNextServiceManager(wrapped_self)
        try:
            findModule = sm.findModule
        except AttributeError:
            # The only service manager that doesn't implement this
            # interface is the global service manager.  There is no
            # direct way to ask if sm is the global service manager.
            return None
        return findModule(name)

    def __import(wrapped_self, module_name):

        mod = wrapped_self.findModule(module_name)
        if mod is None:
            mod = sys.modules.get(module_name)
            if mod is None:
                raise ImportError(module_name)

        return mod

ServiceManager = SiteManager # Backward compat

class ServiceRegistration(ComponentRegistration):
    """Registrations for named components.

    This configures components that live in folders, by name.
    """

    serviceType = zapi.servicenames.Services

    zope.interface.implements(IServiceRegistration)

    def __init__(self, name, path, context=None):
        ComponentRegistration.__init__(self, path, None)
        self.name = name

        if context is not None:
            # Check that the object implements stuff we need
            self.__parent__ = context
            service = self.getComponent()
            if not ILocalService.providedBy(service):
                raise TypeError(
                    "service %r doesn't implement ILocalService" %
                    service)
        # Else, this must be a hopeful test invocation

    def getInterface(self):
        service_manager = getServiceManager(self)
        return service_manager.getInterfaceFor(self.name)


    def activated(self):
        service = self.getComponent()
        if IBindingAware.providedBy(service):
            service.bound(self.name)


    def deactivated(self):
        service = self.getComponent()
        if IBindingAware.providedBy(service):
            service.unbound(self.name)


    def usageSummary(self):
        return self.name + " Service"


# XXX Pickle backward compatability
ServiceConfiguration = ServiceRegistration

# Fssync stuff

_smattrs = (
    '_modules',                         # PersistentModuleRegistry
    '_bindings',
)

class ServiceManagerAdapter(DirectoryAdapter):

    def extra(self):
        obj = removeAllProxies(self.context)
        return AttrMapping(obj, _smattrs)

#BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB


def fixup(event):
    database = event.database
    connection = database.open()
    app = connection.root().get('Application')
    if app is None:
        # no old site
        return

    try:
        sm = app.getSiteManager()
    except ComponentLookupError:
        # no old site
        return

    if hasattr(sm, 'next'):
        # already done
        return
    
    print "Fixing up sites that don't have next pointers"
    fixfolder(app)
    get_transaction().commit()
    connection.close()
    
fixup = Subscriber(fixup)

def fixfolder(folder):
    try:
        sm = folder.getSiteManager()
    except ComponentLookupError:
        pass # nothing to do
    else:
        sm._setNext(folder)
        sm.subSites = ()
        for name in ('Views', 'Adapters'):
            if name in sm._bindings:
                del sm._bindings[name]

    for item in folder.values():
        if IPossibleSite.providedBy(item):
            fixfolder(item)
