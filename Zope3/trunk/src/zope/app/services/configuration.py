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

$Id: configuration.py,v 1.34 2003/06/12 17:03:44 gvanrossum Exp $
"""
__metaclass__ = type


# XXX Backward Compatibility for pickles
import sys
sys.modules['zope.app.services.configurationmanager'
            ] = sys.modules['zope.app.services.configuration']

from persistence import Persistent
from zope.interface import implements
from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.container import IAddNotifiable, IDeleteNotifiable
from zope.app.interfaces.container import IZopeWriteContainer
from zope.app.interfaces.dependable import IDependable, DependencyError

from zope.app.interfaces.services.configuration import IConfigurationManager
from zope.app.interfaces.services.configuration import IConfigurationRegistry
from zope.app.interfaces.services.configuration \
     import INameComponentConfigurable
from zope.app.interfaces.services.configuration import INamedConfiguration
from zope.app.interfaces.services.configuration import IConfiguration
from zope.app.interfaces.services.configuration \
     import INamedComponentConfiguration
from zope.app.interfaces.services.configuration import INameConfigurable
from zope.app.interfaces.services.configuration \
     import INamedComponentConfiguration, IComponentConfiguration
from zope.app.interfaces.services.configuration import IUseConfiguration
from zope.app.interfaces.services.configuration \
     import NoConfigurationManagerError
from zope.app.interfaces.services.configuration import NoLocalServiceError

from zope.app.interfaces.services.configuration import Unregistered
from zope.app.interfaces.services.configuration import Registered, Active
from zope.app.traversing import getRoot, getPath, traverse
from zope.component import getAdapter, queryAdapter
from zope.component import getServiceManager
from zope.app.context import ContextWrapper
from zope.context import ContextMethod, ContextDescriptor, getWrapperContainer
from zope.proxy import removeAllProxies
from zope.security.checker import InterfaceChecker
from zope.security.proxy import Proxy, trustedRemoveSecurityProxy
from zope.proxy import getProxiedObject

class ConfigurationStatusProperty(ContextDescriptor):

    def __init__(self, service):
        self.service = service

    def __get__(self, inst, klass):
        if inst is None:
            return self

        configuration = inst

        sm = getServiceManager(configuration)
        service = sm.queryLocalService(self.service)
        # XXX The following may fail; there's a subtle bug here when
        # the returned service isn't in the same service manager as
        # the one owning the configuration.
        registry = service and service.queryConfigurationsFor(configuration)

        if registry:

            if registry.active() == configuration:
                return Active
            if registry.registered(configuration):
                return Registered

        return Unregistered

    def __set__(self, inst, value):
        configuration = inst

        sm = getServiceManager(configuration)
        service = sm.queryLocalService(self.service)

        registry = service and service.queryConfigurationsFor(configuration)

        if value == Unregistered:
            if registry:
                registry.unregister(configuration)

        else:
            if not service:
                raise NoLocalServiceError(
                    "This configuration change cannot be performed because "
                    "there isn't a corresponding %s service defined in this "
                    "site. To proceed, first add a local %s service."
                    % (self.service, self.service))

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

    implements(IConfigurationRegistry)

    _data = ()

    def _id(self, ob):

        # Get and check relative path
        path = getPath(ob)
        prefix = "/++etc++site/"
        lpackages = path.rfind(prefix)
        if lpackages < 0:
            # XXX Backward compatability
            prefix = "/++etc++Services/"
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
    implementedBy(SimpleConfiguration) or explicitly implementing
    IDeleteNotifiable.
    """

    implements(IConfiguration, IDeleteNotifiable,
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
                objectpath = getPath(configuration)
            except: # XXX
                objectpath = str(configuration)
            raise DependencyError("Can't delete active configuration (%s)"
                                  % objectpath)
        elif objectstatus == Registered:
            configuration.status = Unregistered


class NamedConfiguration(SimpleConfiguration):
    """Named configuration
    """

    implements(INamedConfiguration)

    def __init__(self, name):
        self.name = name

    def usageSummary(self):
        return "%s %s" % (self.name, self.__class__.__name__)


class ComponentConfiguration(SimpleConfiguration):
    """Component configuration.

    Subclasses should define a getInterface() method returning the interface
    of the component.
    """

    # SimpleConfiguration implements IDeleteNotifiable, so we don't need
    # it below.
    implements(IComponentConfiguration, IAddNotifiable)

    def __init__(self, component_path, permission=None):
        self.componentPath = component_path
        if permission == 'zope.Public':
            permission = CheckerPublic
        self.permission = permission

    def implementationSummary(self):
        return self.componentPath

    def getComponent(wrapped_self):
        service_manager = getServiceManager(wrapped_self)

        # The user of the configuration object may not have permission
        # to traverse to the component.  Yet they should be able to
        # get it by calling getComponent() on a configuration object
        # for which they do have permission.  What they get will be
        # wrapped in a security proxy of course.  Hence:

        # We have to be clever here. We need to do an honest to
        # god unrestricted traveral, which means we have to
        # traverse from an unproxied object. But, it's not enough
        # for the service manager to be unproxied, because the
        # path is an absolute path. When absolute paths are
        # traversed, the traverser finds the physical root and
        # traverses from there, so we need to make sure the
        # physical root isn't proxied.

        path = wrapped_self.componentPath
        # Get the root and unproxy it
        root = removeAllProxies(getRoot(service_manager))
        if path.startswith("/"):
            # Absolute path
            component = traverse(root, path)
        else:
            # Relative path.
            # XXX We do a strange little dance because we want the
            #     context to inherit the unproxied root, and this is
            #     the only way to keep it.
            ancestor = getWrapperContainer(getWrapperContainer(wrapped_self))
            ancestor = traverse(root, getPath(ancestor))
            component = traverse(ancestor, path)

        if wrapped_self.permission:
            if type(component) is Proxy:
                # There should be at most one security Proxy around an object.
                # So, if we're going to add a new security proxy, we need to
                # remove any existing one.
                component = trustedRemoveSecurityProxy(component)

            interface = wrapped_self.getInterface()

            checker = InterfaceChecker(interface, wrapped_self.permission)

            component = Proxy(component, checker)

        return component
    getComponent = ContextMethod(getComponent)

    def afterAddHook(self, configuration, container):
        "See IAddNotifiable"
        component = configuration.getComponent()
        dependents = getAdapter(component, IDependable)
        objectpath = getPath(configuration)
        dependents.addDependent(objectpath)
        # Also update usage, if supported
        adapter = queryAdapter(component, IUseConfiguration)
        if adapter is not None:
            adapter.addUsage(getPath(configuration))

    def beforeDeleteHook(self, configuration, container):
        "See IDeleteNotifiable"
        super(ComponentConfiguration, self).beforeDeleteHook(configuration,
                                                             container)
        component = configuration.getComponent()
        dependents = getAdapter(component, IDependable)
        objectpath = getPath(configuration)
        dependents.removeDependent(objectpath)
        # Also update usage, if supported
        adapter = queryAdapter(component, IUseConfiguration)
        if adapter is not None:
            adapter.removeUsage(getPath(configuration))

class NamedComponentConfiguration(NamedConfiguration, ComponentConfiguration):
    """Configurations for named components.

    This configures components that live in folders, by name.
    """
    implements(INamedComponentConfiguration)

    def __init__(self, name, component_path, permission=None):
        NamedConfiguration.__init__(self, name)
        ComponentConfiguration.__init__(self, component_path, permission)


class NameConfigurable:
    """Mixin for implementing INameConfigurable
    """
    implements(INameConfigurable)

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
    implements(INameComponentConfigurable)

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

    implements(IUseConfiguration)

    def __init__(self, context):
        self.context = context

    def addUsage(self, location):
        annotations = getAdapter(self.context, IAnnotations)
        annotations[USE_CONFIG_KEY] = (annotations.get(USE_CONFIG_KEY, ()) +
                                       (location, ))

    def removeUsage(self, location):
        annotations = getAdapter(self.context, IAnnotations)
        locations = annotations.get(USE_CONFIG_KEY, ())
        if locations:
            locs = tuple([loc for loc in locations if loc != location])
            if locs != locations:
                if locs:
                    annotations[USE_CONFIG_KEY] = locs
                else:
                    del annotations[USE_CONFIG_KEY]

    def usages(self):
        annotations = getAdapter(self.context, IAnnotations)
        return annotations.get(USE_CONFIG_KEY, ())

class ConfigurationManager(Persistent):
    """Configuration manager

    Manages configurations within a package.
    """

    implements(IConfigurationManager, IDeleteNotifiable)

    def __init__(self):
        self._data = ()
        self._next = 0

    def __getitem__(self, key):
        "See IItemContainer"
        v = self.get(key)
        if v is None:
            raise KeyError, key
        return v

    def get(self, key, default=None):
        "See IReadMapping"
        for k, v in self._data:
            if k == key:
                return v
        return default

    def __contains__(self, key):
        "See IReadMapping"
        return self.get(key) is not None


    def keys(self):
        "See IEnumerableMapping"
        return [k for k, v in self._data]

    def __iter__(self):
        return iter(self.keys())

    def values(self):
        "See IEnumerableMapping"
        return [v for k, v in self._data]

    def items(self):
        "See IEnumerableMapping"
        return self._data

    def __len__(self):
        "See IEnumerableMapping"
        return len(self._data)

    def setObject(self, key, object):
        "See IWriteContainer"
        self._next += 1
        if key:
            if key in self:
                raise DuplicationError("key is already registered", key)
            try:
                n = int(key)
            except ValueError:
                pass
            else:
                if n > self._next:
                    self._next = n
        else:
            key = str(self._next)
            while key in self:
                self._next += 1
                key = str(self._next)
        self._data += ((key, object), )
        return key

    def __delitem__(self, key):
        "See IWriteContainer"
        if key not in self:
            raise KeyError, key
        self._data = tuple(
            [item
             for item in self._data
             if item[0] != key]
            )

    def moveTop(self, names):
        self._data = tuple(
            [item for item in self._data if (item[0] in names)]
            +
            [item for item in self._data if (item[0] not in names)]
            )

    def moveBottom(self, names):
        self._data = tuple(
            [item for item in self._data if (item[0] not in names)]
            +
            [item for item in self._data if (item[0] in names)]
            )

    def _moveUpOrDown(self, names, direction):
        # Move each named item by one position. Note that this
        # might require moving some unnamed objects by more than
        # one position.

        indexes = {}

        # Copy named items to positions one less than they currently have
        i = -1
        for item in self._data:
            i += 1
            if item[0] in names:
                j = max(i + direction, 0)
                while j in indexes:
                    j += 1

                indexes[j] = item

        # Fill in the rest where there's room.
        i = 0
        for item in self._data:
            if item[0] not in names:
                while i in indexes:
                    i += 1
                indexes[i] = item

        items = indexes.items()
        items.sort()

        self._data = tuple([item[1] for item in items])

    def moveUp(self, names):
        self._moveUpOrDown(names, -1)

    def moveDown(self, names):
        self._moveUpOrDown(names, 1)

    def beforeDeleteHook(self, object, container):
        assert object == self
        container = getAdapter(object, IZopeWriteContainer)
        for k, v in self._data:
            del container[k]


class ConfigurationManagerContainer(object):
    """Mix-in to implement IConfigurationManagerContainer
    """

    def __init__(self):
        super(ConfigurationManagerContainer, self).__init__()
        self.setObject('RegistrationManager', ConfigurationManager())

    def __delitem__(self, name):
        """Delete an item, but not if it's the last configuration manager
        """
        item = self[name]
        if IConfigurationManager.isImplementedBy(item):
            # Check to make sure it's not the last one
            if len([i for i in self.values()
                    if IConfigurationManager.isImplementedBy(i)]) < 2:
                raise NoConfigurationManagerError(
                    "Can't delete the last configuration manager")
        super(ConfigurationManagerContainer, self).__delitem__(name)

    def getConfigurationManager(self):
        """Get a configuration manager
        """
        # Get the configuration manager for this folder
        for name in self:
            item = self[name]
            if IConfigurationManager.isImplementedBy(item):
                # We found one. Get it in context
                return ContextWrapper(item, self, name=name)
        else:
            raise NoConfigurationManagerError(
                "Couldn't find an configuration manager")
    getConfigurationManager = ContextMethod(getConfigurationManager)


from zope.xmlpickle import dumps, loads
from zope.app.interfaces.fssync import IObjectFile
from zope.app.fssync.classes import ObjectEntryAdapter

class ComponentConfigurationAdapter(ObjectEntryAdapter):

    """Fssync adapter for ComponentConfiguration objects and subclasses.

    This is fairly generic -- it should apply to most subclasses of
    ComponentConfiguration.  But in order for it to work for a
    specific subclass (say, UtilityConfiguration), you have to (a) add
    an entry to configure.zcml, like this:

        <fssync:adapter
            class=".utility.UtilityConfiguration"
            factory=".configuration.ComponentConfigurationAdapter"
            />

    and (b) add a function to factories.py, like this:

        def UtilityConfiguration():
            from zope.app.services.utility import UtilityConfiguration
            return UtilityConfiguration("", None, "")

    The file representation of a configuration object is an XML pickle
    for a modified version of the instance dict.  In this version of
    the instance dict, the __annotations__ attribute is omitted,
    because annotations are already stored on the filesystem in a
    different way (in @@Zope/Annotations/<file>).
    """

    implements(IObjectFile)

    def factory(self):
        """See IObjectEntry."""
        name = self.context.__class__.__name__
        return "zope.app.services.factories." + name

    def getBody(self):
        """See IObjectEntry."""
        obj = removeAllProxies(self.context)
        ivars = {}
        ivars.update(obj.__getstate__())
        aname = "__annotations__"
        if aname in ivars:
            del ivars[aname]
        return dumps(ivars)

    def setBody(self, body):
        """See IObjectEntry."""
        obj = removeAllProxies(self.context)
        ivars = loads(body)
        obj.__setstate__(ivars)
