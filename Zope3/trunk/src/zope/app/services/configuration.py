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
"""Component registration support for services

$Id: configuration.py,v 1.12 2003/03/18 21:02:22 jim Exp $
"""
__metaclass__ = type

from persistence import Persistent

from zope.app.interfaces.annotation import IAttributeAnnotatable

from zope.component \
     import getAdapter, getService, queryService, getServiceManager

from zope.proxy.context import ContextMethod, ContextWrapper
from zope.proxy.introspection import removeAllProxies

from zope.security.checker import InterfaceChecker
from zope.security.proxy import Proxy

from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.container import IAddNotifiable, IDeleteNotifiable
from zope.app.interfaces.dependable import IDependable, DependencyError

from zope.app.interfaces.services.configuration import IConfigurationRegistry
from zope.app.interfaces.services.configuration \
     import INameComponentConfigurable, INamedConfiguration, IConfiguration
from zope.app.interfaces.services.configuration \
     import INamedComponentConfiguration, INameConfigurable
from zope.app.interfaces.services.configuration import IUseConfiguration
from zope.app.interfaces.services.configuration \
     import Unregistered, Registered, Active

from zope.app.traversing \
     import getPhysicalRoot, getPhysicalPathString, traverse, locationAsUnicode


class ConfigurationStatusProperty:

    __Zope_ContextWrapper_contextful_get__ = True
    __Zope_ContextWrapper_contextful_set__ = True

    def __init__(self, service):
        self.service = service

    def __get__(self, inst, klass):
        if inst is None:
            return self

        configuration = inst
        service = queryService(configuration, self.service)
        registry = service and service.queryConfigurationsFor(configuration)

        if registry:

            if registry.active() == configuration:
                return Active
            if registry.registered(configuration):
                return Registered

        return Unregistered

    def __set__(self, inst, value):
        configuration = inst
        service = queryService(configuration, self.service)
        registry = service and service.queryConfigurationsFor(configuration)

        if value == Unregistered:
            if registry:
                registry.unregister(configuration)

        else:
            if not service:
                # raise an error
                service = getService(configuration, self.service)

            if registry is None:
                registry = service.createConfigurationsFor(configuration)

            if value == Registered:
                if registry.active() == configuration:
                    registry.deactivate(configuration)
                else:
                    registry.register(configuration)

            elif value == Active:
                if not registry.registered(configuration):
                    registry.register(configuration)
                registry.activate(configuration)


class ConfigurationRegistry(Persistent):

    __implements__ = IConfigurationRegistry

    _data = ()

    def _id(self, ob):

        # Get and check relative path
        prefix = "/++etc++Services/"
        path = getPhysicalPathString(ob)
        lpackages = path.rfind(prefix)
        if lpackages < 0:
            raise ValueError("Configuration object is in an invalid location",
                             path)

        rpath = path[lpackages+len(prefix):]
        if not rpath or (".." in rpath.split("/")):
            raise ValueError("Configuration object is in an invalid location",
                             path)

        return rpath

    def register(wrapped_self, configuration):
        cid = wrapped_self._id(configuration)

        if wrapped_self._data:
            if cid in wrapped_self._data:
                return # already registered
        else:
            # Nothing registered. Need to stick None in front so that nothing
            # is active.
            wrapped_self._data = (None, )

        wrapped_self._data += (cid, )
    register = ContextMethod(register)

    def unregister(wrapped_self, configuration):
        cid = wrapped_self._id(configuration)

        data = wrapped_self._data
        if data:
            if data[0] == cid:
                # It's active, we need to switch in None
                data = (None, ) + data[1:]

                # we need to notify it that it's inactive.
                configuration.deactivated()

            else:
                data = tuple([item for item in data if item != cid])

        # Check for empty registry
        if len(data) == 1 and data[0] is None:
            data = ()

        wrapped_self._data = data
    unregister = ContextMethod(unregister)

    def registered(wrapped_self, configuration):
        cid = wrapped_self._id(configuration)
        return cid in wrapped_self._data
    registered = ContextMethod(registered)

    def activate(wrapped_self, configuration):
        cid = wrapped_self._id(configuration)
        data = wrapped_self._data

        if cid in data:

            if data[0] == cid:
                return # already active

            if data[0] is None:
                # Remove leading None marker
                data = data[1:]
            else:
                # We need to deactivate the currently active component
                sm = getServiceManager(wrapped_self)
                old = traverse(sm, data[0])
                old.deactivated()


            wrapped_self._data = (cid, ) + tuple(
                [item for item in data if item != cid]
                )

            configuration.activated()

        else:
            raise ValueError(
                "Configuration to be activated is not registered",
                configuration)
    activate = ContextMethod(activate)

    def deactivate(wrapped_self, configuration):
        cid = wrapped_self._id(configuration)

        if cid in wrapped_self._data:

            if wrapped_self._data[0] != cid:
                return # already inactive

            # Just stick None on the front
            wrapped_self._data = (None, ) + wrapped_self._data

            configuration.deactivated()

        else:
            raise ValueError(
                "Configuration to be deactivated is not registered",
                configuration)
    deactivate = ContextMethod(deactivate)

    def active(wrapped_self):
        if wrapped_self._data:
            path = wrapped_self._data[0]
            if path is not None:
                # Make sure we can traverse to it.
                sm = getServiceManager(wrapped_self)
                configuration = traverse(sm, path)
                return configuration

        return None
    active = ContextMethod(active)

    def __nonzero__(self):
        return bool(self._data)

    def info(wrapped_self):
        sm = getServiceManager(wrapped_self)

        result = [{'id': path,
                   'active': False,
                   'configuration': (path and traverse(sm, path))
                   }
                  for path in wrapped_self._data
                  ]

        if result:
            if result[0]['configuration'] is None:
                del result[0]
            else:
                result[0]['active'] = True

        return result
    info = ContextMethod(info)


class SimpleConfiguration(Persistent):
    """Configuration objects that just contain configuration data

    Classes that derive from this must make sure they implement
    IDeleteNotifiable either by implementing
    SimpleConfiguration.__implements__ or explicitly implementing
    IDeleteNotifiable.
    """

    __implements__ = (IConfiguration, IDeleteNotifiable,
                      # We are including this here because we want all of the
                      # subclasses to get it and we don't really need to be
                      # flexible about the policy here. At least we don't
                      # *think* we do. :)
                      IAttributeAnnotatable,
                      )

    # Methods from IConfiguration

    def activated(self):
        pass

    def deactivated(self):
        pass

    def usageSummary(self):
        return self.__class__.__name__

    def implementationSummary(self):
        return ""

    # Methods from IDeleteNotifiable

    def beforeDeleteHook(self, configuration, container):
        "See IDeleteNotifiable"

        objectstatus = configuration.status

        if objectstatus == Active:
            try:
                objectpath = getPhysicalPathString(configuration)
            except: # XXX
                objectpath = str(configuration)
            raise DependencyError("Can't delete active configuration (%s)"
                                  % objectpath)
        elif objectstatus == Registered:
            configuration.status = Unregistered


class NamedConfiguration(SimpleConfiguration):
    """Named configuration
    """

    __implements__ = INamedConfiguration, SimpleConfiguration.__implements__

    def __init__(self, name):
        self.name = name
        super(NamedConfiguration, self).__init__()

    def usageSummary(self):
        return "%s %s" % (self.name, self.__class__.__name__)


class NamedComponentConfiguration(NamedConfiguration):
    """Named component configuration

    Subclasses should define a getInterface() method returning the interface
    of the component.
    """

    # NamedConfiguration.__implements__ includes IDeleteNotifiable
    __implements__ = (INamedComponentConfiguration,
                      NamedConfiguration.__implements__, IAddNotifiable)

    def __init__(self, name, component_path, permission=None):
        self.componentPath = component_path
        if permission == 'zope.Public':
            permission = CheckerPublic
        self.permission = permission
        super(NamedComponentConfiguration, self).__init__(name)

    def implementationSummary(self):
        return locationAsUnicode(self.componentPath)

    def getComponent(wrapped_self):
        service_manager = getServiceManager(wrapped_self)

        # We have to be clever here. We need to do an honest to
        # god unrestricted traveral, which means we have to
        # traverse from an unproxied object. But, it's not enough
        # for the service manager to be unproxied, because the
        # path is an absolute path. When absolute paths are
        # traversed, the traverser finds the physical root and
        # traverses from there, so we need to make sure the
        # physical root isn't proxied.

        # get the root and unproxy it.
        root = removeAllProxies(getPhysicalRoot(service_manager))
        component = traverse(root, wrapped_self.componentPath)

        if wrapped_self.permission:
            if type(component) is Proxy:
                # There should be at most one security Proxy around an object.
                # So, if we're going to add a new security proxy, we need to
                # remove any existing one.
                component = removeSecurityProxy(component)

            interface = wrapped_self.getInterface()

            checker = InterfaceChecker(interface, wrapped_self.permission)

            component = Proxy(component, checker)

        return component
    getComponent = ContextMethod(getComponent)

    def afterAddHook(self, configuration, container):
        "See IAddNotifiable"
        component = configuration.getComponent()
        dependents = getAdapter(component, IDependable)
        objectpath = getPhysicalPathString(configuration)
        dependents.addDependent(objectpath)

    def beforeDeleteHook(self, configuration, container):
        "See IDeleteNotifiable"
        super(NamedComponentConfiguration, self
              ).beforeDeleteHook(configuration, container)
        component = configuration.getComponent()
        dependents = getAdapter(component, IDependable)
        objectpath = getPhysicalPathString(configuration)
        dependents.removeDependent(objectpath)


class NameConfigurable:
    """Mixin for implementing INameConfigurable
    """

    __implements__ = INameConfigurable

    def __init__(self, *args, **kw):
        self._bindings = {}
        super(NameConfigurable, self).__init__(*args, **kw)

    def queryConfigurationsFor(wrapped_self, cfg, default=None):
        """See IConfigurable"""
        return wrapped_self.queryConfigurations(cfg.name, default)
    queryConfigurationsFor = ContextMethod(queryConfigurationsFor)

    def queryConfigurations(wrapped_self, name, default=None):
        """See INameConfigurable"""
        registry = wrapped_self._bindings.get(name, default)
        return ContextWrapper(registry, wrapped_self)
    queryConfigurations = ContextMethod(queryConfigurations)

    def createConfigurationsFor(wrapped_self, cfg):
        """See IConfigurable"""
        return wrapped_self.createConfigurations(cfg.name)
    createConfigurationsFor = ContextMethod(createConfigurationsFor)

    def createConfigurations(wrapped_self, name):
        """See INameConfigurable"""
        try:
            registry = wrapped_self._bindings[name]
        except KeyError:
            wrapped_self._bindings[name] = registry = ConfigurationRegistry()
            wrapped_self._p_changed = 1
        return ContextWrapper(registry, wrapped_self)
    createConfigurations = ContextMethod(createConfigurations)

    def listConfigurationNames(wrapped_self):
        """See INameConfigurable"""
        return filter(wrapped_self._bindings.get,
                      wrapped_self._bindings.keys())


class NameComponentConfigurable(NameConfigurable):
    """Mixin for implementing INameComponentConfigurable
    """

    __implements__ = INameComponentConfigurable

    def queryActiveComponent(wrapped_self, name, default=None):
        """See INameComponentConfigurable"""
        registry = wrapped_self.queryConfigurations(name)
        if registry:
            configuration = registry.active()
            if configuration is not None:
                return configuration.getComponent()
        return default
    queryActiveComponent = ContextMethod(queryActiveComponent)


USE_CONFIG_KEY = 'zope.app.services.configuration.UseConfiguration'

class UseConfiguration:
    """An adapter."""

    __implements__ = IUseConfiguration

    def __init__(self, context):
        self.context = context

    def addUsage(self, location):
        annotations = getAdapter(self.context, IAnnotations)
        annotations[USE_CONFIG_KEY] = (annotations.get(USE_CONFIG_KEY, ()) +
                                       (location, ))

    def removeUsage(self, location):
        annotations = getAdapter(self.context, IAnnotations)
        locs = [loc for loc in annotations.get(USE_CONFIG_KEY, ())
                    if loc != location]
        annotations[USE_CONFIG_KEY] = tuple(locs)

    def usages(self):
        annotations = getAdapter(self.context, IAnnotations)
        return annotations.get(USE_CONFIG_KEY, ())
