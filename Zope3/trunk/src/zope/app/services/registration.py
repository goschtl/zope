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

$Id: registration.py,v 1.21 2004/02/20 16:57:30 fdrake Exp $
"""
__metaclass__ = type

from zope.app import zapi

from persistent import Persistent
from zope.interface import implements
from zope.fssync.server.interfaces import IObjectFile
from zope.fssync.server.entryadapter import ObjectEntryAdapter
from zope.proxy import removeAllProxies, getProxiedObject
from zope.security.checker import InterfaceChecker, CheckerPublic
from zope.security.proxy import Proxy, trustedRemoveSecurityProxy
from zope.exceptions import DuplicationError
from zope.xmlpickle import dumps, loads

from zope.app.container.contained import Contained
from zope.app.container.contained import setitem, contained, uncontained
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.container import IAddNotifiable, IRemoveNotifiable
from zope.app.interfaces.dependable import IDependable, DependencyError
from zope.app.interfaces.services import registration as interfaces
from zope.app.interfaces.services.module import IModuleManager


class RegistrationStatusProperty(object):

    def __get__(self, inst, klass):
        if inst is None:
            return self

        registration = inst
        service = self._get_service(registration)
        registry = service and service.queryRegistrationsFor(registration)

        if registry:

            if registry.active() == registration:
                return interfaces.ActiveStatus
            if registry.registered(registration):
                return interfaces.RegisteredStatus

        return interfaces.UnregisteredStatus

    def __set__(self, inst, value):
        registration = inst
        service = self._get_service(registration)
        registry = service and service.queryRegistrationsFor(registration)

        if value == interfaces.UnregisteredStatus:
            if registry:
                registry.unregister(registration)

        else:
            if not service:
                raise interfaces.NoLocalServiceError(
                    "This registration change cannot be performed because "
                    "there isn't a corresponding %s service defined in this "
                    "site. To proceed, first add a local %s service."
                    % (registration.serviceType, registration.serviceType))

            if registry is None:
                registry = service.createRegistrationsFor(registration)

            if value == interfaces.RegisteredStatus:
                if registry.active() == registration:
                    registry.deactivate(registration)
                else:
                    registry.register(registration)

            elif value == interfaces.ActiveStatus:
                if not registry.registered(registration):
                    registry.register(registration)
                registry.activate(registration)

    def _get_service(self, registration):
        # how we get the service is factored out so subclasses can
        # approach this differently
        sm = zapi.getServiceManager(registration)
        return sm.queryLocalService(registration.serviceType)


class RegistrationStack(Persistent, Contained):

    """Registration registry implementation.

    The invariants for _data are as follows:

        (1) The last element (if any) is not None

        (2) No value occurs more than once

        (3) Each value except None is a relative path from the nearest
            service manager to an object implementing IRegistration
    """

    implements(interfaces.IRegistrationStack)

    _data = ()  # tuple of strings (ivar)

    def __init__(self, container):
        self.__parent__ = container

    def _id(self, ob):
        """Turn ob into a path relative to the site management folder."""
        # Get and check relative path
        path = zapi.getPath(ob)
        prefix = "/++etc++site/"
        lpackages = path.rfind(prefix)
        if lpackages < 0:
            # XXX Backward compatability
            prefix = "/++etc++Services/"
            lpackages = path.rfind(prefix)

        if lpackages < 0:
            raise ValueError("Registration object is in an invalid location",
                             path)

        rpath = path[lpackages+len(prefix):]
        if not rpath or (".." in rpath.split("/")):
            raise ValueError("Registration object is in an invalid location",
                             path)

        return rpath

    def register(self, registration):
        cid = self._id(registration)

        if self._data:
            if cid in self._data:
                return # already registered
        else:
            # Nothing registered. Need to stick None in front so that nothing
            # is active.
            self._data = (None, )

        self._data += (cid, )

    def unregister(self, registration):
        cid = self._id(registration)

        data = self._data
        if data:
            if data[0] == cid:
                data = data[1:]
                self._data = data

                # Tell it that it is no longer active
                registration.deactivated()

                if data and data[0] is not None:
                    # Activate the newly active component
                    sm = zapi.getServiceManager(self)
                    new = zapi.traverse(sm, data[0])
                    new.activated()
            else:
                # Remove it from our data
                data = tuple([item for item in data if item != cid])

                # Check for trailing None
                if data and data[-1] is None:
                    data = data[:-1]

                self._data = data

    def registered(self, registration):
        cid = self._id(registration)
        return cid in self._data

    def activate(self, registration):
        if registration is None:
            cid = None
        else:
            cid = self._id(registration)
        data = self._data

        if cid is None and not data:
            return # already in the state we want

        if cid is None or cid in data:
            old = data[0]
            if old == cid:
                return # already active

            # Insert it in front, removing it from back
            data = (cid, ) + tuple([item for item in data if item != cid])

            # Check for trailing None
            if data[-1] == None:
                data = data[:-1]

            # Write data back
            self._data = data

            if old is not None:
                # Deactivated the currently active component
                sm = zapi.getServiceManager(self)
                old = zapi.traverse(sm, old)
                old.deactivated()

            if registration is not None:
                # Tell it that it is now active
                registration.activated()

        else:
            raise ValueError(
                "Registration to be activated is not registered",
                registration)

    def deactivate(self, registration):
        cid = self._id(registration)
        data = self._data

        if cid not in data:
            raise ValueError(
                "Registration to be deactivated is not registered",
                registration)

        if data[0] != cid:
            return # already inactive

        if None not in data:
            # Append None
            data += (None,)

        # Move it to the end
        data = data[1:] + data[:1]

        # Write data back
        self._data = data

        # Tell it that it is no longer active
        registration.deactivated()

        if data[0] is not None:
            # Activate the newly active component
            sm = zapi.getServiceManager(self)
            new = zapi.traverse(sm, data[0])
            new.activated()

    def active(self):
        if self._data:
            path = self._data[0]
            if path is not None:
                # Make sure we can zapi.traverse to it.
                sm = zapi.getServiceManager(self)
                registration = zapi.traverse(sm, path)
                return registration

        return None

    def __nonzero__(self):
        return bool(self._data)

    def info(self, keep_dummy=False):
        sm = zapi.getServiceManager(self)

        data = self._data
        if None not in data:
            data += (None,)

        result = [{'id': path or "",
                   'active': False,
                   'registration': (path and zapi.traverse(sm, path))
                  }
                  for path in data
                 ]

        result[0]['active'] = True

        if not keep_dummy:
            # Throw away dummy:
            result = [x for x in result if x['id']]

        return result

class NotifyingRegistrationStack(RegistrationStack):

    def activate(self, registration):
        RegistrationStack.activate(self, registration)
        self.__parent__.notifyActivated(self, registration)

    def deactivate(self, registration):
        RegistrationStack.deactivate(self, registration)
        self.__parent__.notifyDeactivated(self, registration)

class SimpleRegistration(Persistent, Contained):
    """Registration objects that just contain registration data

    Classes that derive from this must make sure they implement
    IRemoveNotifiable either by implementing
    implementedBy(SimpleRegistration) or explicitly implementing
    IRemoveNotifiable.
    """

    implements(interfaces.IRegistration, IRemoveNotifiable,
               # We are including this here because we want all of the
               # subclasses to get it and we don't really need to be
               # flexible about the policy here. At least we don't
               # *think* we do. :)
               IAttributeAnnotatable,
               )

    status = RegistrationStatusProperty()

    # Methods from IRegistration

    def activated(self):
        pass

    def deactivated(self):
        pass

    def usageSummary(self):
        return self.__class__.__name__

    def implementationSummary(self):
        return ""

    # Methods from IRemoveNotifiable

    def removeNotify(self, event):
        "See IRemoveNotifiable"

        objectstatus = self.status

        if objectstatus == interfaces.ActiveStatus:
            try:
                objectpath = zapi.getPath(self)
            except: # XXX
                objectpath = str(self)
            raise DependencyError("Can't delete active registration (%s)"
                                  % objectpath)
        elif objectstatus == interfaces.RegisteredStatus:
            self.status = interfaces.UnregisteredStatus


class NamedRegistration(SimpleRegistration):
    """Named registration
    """

    implements(interfaces.INamedRegistration)

    def __init__(self, name):
        self.name = name

    def usageSummary(self):
        return "%s %s" % (self.name, self.__class__.__name__)


class ComponentRegistration(SimpleRegistration):
    """Component registration.

    Subclasses should define a getInterface() method returning the interface
    of the component.
    """

    # SimpleRegistration implements IRemoveNotifiable, so we don't need
    # it below.
    implements(interfaces.IComponentRegistration, IAddNotifiable)

    def __init__(self, component_path, permission=None):
        self.componentPath = component_path
        if permission == 'zope.Public':
            permission = CheckerPublic
        self.permission = permission

    def implementationSummary(self):
        return self.componentPath

    def getComponent(self):
        service_manager = zapi.getServiceManager(self)

        # The user of the registration object may not have permission
        # to traverse to the component.  Yet they should be able to
        # get it by calling getComponent() on a registration object
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

        path = self.componentPath
        # Get the root and unproxy it
        if path.startswith("/"):
            # Absolute path
            root = removeAllProxies(zapi.getRoot(service_manager))
            component = zapi.traverse(root, path)
        else:
            # Relative path.
            ancestor = self.__parent__.__parent__
            component = zapi.traverse(ancestor, path)

        if self.permission:
            if type(component) is Proxy:
                # There should be at most one security Proxy around an object.
                # So, if we're going to add a new security proxy, we need to
                # remove any existing one.
                component = trustedRemoveSecurityProxy(component)

            interface = self.getInterface()

            checker = InterfaceChecker(interface, self.permission)

            component = Proxy(component, checker)

        return component

    def addNotify(self, event):
        "See IAddNotifiable"
        component = self.getComponent()
        dependents = zapi.getAdapter(component, IDependable)
        objectpath = zapi.getPath(self)
        dependents.addDependent(objectpath)
        # Also update usage, if supported
        adapter = zapi.queryAdapter(component, interfaces.IRegistered)
        if adapter is not None:
            adapter.addUsage(objectpath)

    def removeNotify(self, event):
        "See IRemoveNotifiable"
        super(ComponentRegistration, self).removeNotify(event)
        component = self.getComponent()
        dependents = zapi.getAdapter(component, IDependable)
        objectpath = zapi.getPath(self)
        dependents.removeDependent(objectpath)
        # Also update usage, if supported
        adapter = zapi.queryAdapter(component, interfaces.IRegistered)
        if adapter is not None:
            adapter.removeUsage(zapi.getPath(self))

class NamedComponentRegistration(NamedRegistration, ComponentRegistration):
    """Registrations for named components.

    This configures components that live in folders, by name.
    """
    implements(interfaces.INamedComponentRegistration)

    def __init__(self, name, component_path, permission=None):
        NamedRegistration.__init__(self, name)
        ComponentRegistration.__init__(self, component_path, permission)


class NameRegistry:
    """Mixin for implementing INameRegistry
    """
    implements(interfaces.INameRegistry)

    def __init__(self, *args, **kw):
        self._bindings = {}
        super(NameRegistry, self).__init__(*args, **kw)

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
        """See INameRegistry"""
        try:
            registry = self._bindings[name]
        except KeyError:
            registry = RegistrationStack(self)
            self._bindings[name] = registry
            self._p_changed = 1
        return registry

    def listRegistrationNames(self):
        """See INameRegistry"""
        return filter(self._bindings.get,
                      self._bindings.keys())


class NameComponentRegistry(NameRegistry):
    """Mixin for implementing INameComponentRegistry
    """
    implements(interfaces.INameComponentRegistry)

    def queryActiveComponent(self, name, default=None):
        """See INameComponentRegistry"""
        registry = self.queryRegistrations(name)
        if registry:
            registration = registry.active()
            if registration is not None:
                return registration.getComponent()
        return default


from zope.app.dependable import PathSetAnnotation

class Registered(PathSetAnnotation):
    """An adapter from IRegisterable to IRegistered.

    This class is the only place that knows how 'Registered'
    data is represented.
    """

    implements(interfaces.IRegistered)

    # We want to use this key:
    #   key = "zope.app.services.registration.Registered"
    # But we have existing annotations with the following key, so we'll keep
    # it. :(
    key = "zope.app.services.configuration.UseConfiguration"

    addUsage = PathSetAnnotation.addPath
    removeUsage = PathSetAnnotation.removePath
    usages = PathSetAnnotation.getPaths

    def registrations(self):
        return [zapi.traverse(self.context, path)
                for path in self.getPaths()]


class RegistrationManager(Persistent, Contained):
    """Registration manager

    Manages registrations within a package.
    """

    implements(interfaces.IRegistrationManager, IRemoveNotifiable)

    def __init__(self):
        self._data = ()

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

    def __setitem__(self, key, v):
        setitem(self, self.__setitem, key, v)

    def __setitem(self, key, v):
        if key in self:
            raise DuplicationError(key)
        self._data += ((key, v), )

    def addRegistration(self, object):
        "See IWriteContainer"
        key = self._chooseName('', object)
        self[key] = object
        return key

    def _chooseName(self, name, object):
        if not name:
            name = object.__class__.__name__

        i = 1
        n = name
        while n in self:
            i += 1
            n = name + str(i)

        return n

    def __delitem__(self, key):
        "See IWriteContainer"
        uncontained(self[key], self, key)
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

    def removeNotify(self, event):
        assert event.object == self
        for name in self:
            del self[name]


class RegistrationManagerContainer(object):
    """Mix-in to implement IRegistrationManagerContainer
    """

    implements(interfaces.IRegistrationManagerContainer)

    def __init__(self):
        super(RegistrationManagerContainer, self).__init__()
        rm = RegistrationManager()
        rm.__parent__ = self
        rm.__name__ = 'RegistrationManager'
        self[rm.__name__] = rm

    def __delitem__(self, name):
        """Delete an item, but not if it's the last registration manager
        """
        item = self[name]
        if interfaces.IRegistrationManager.isImplementedBy(item):
            # Check to make sure it's not the last one
            if len([i for i in self.values()
                    if interfaces.IRegistrationManager.isImplementedBy(i)
                    ]
                   ) < 2:
                raise interfaces.NoRegistrationManagerError(
                    "Can't delete the last registration manager")
        super(RegistrationManagerContainer, self).__delitem__(name)

    def getRegistrationManager(self):
        """Get a registration manager
        """
        # Get the registration manager for this folder
        for name in self:
            item = self[name]
            if interfaces.IRegistrationManager.isImplementedBy(item):
                # We found one. Get it in context
                return item
        else:
            raise interfaces.NoRegistrationManagerError(
                "Couldn't find an registration manager")

    def findModule(self, name):
        # Used by the persistent modules import hook

        # Look for a .py file first:
        manager = self.get(name+'.py')
        if manager is not None:
            # found an item with that name, make sure it's a module(manager):
            if IModuleManager.isImplementedBy(manager):
                return manager.getModule()

        # Look for the module in this folder:
        manager = self.get(name)
        if manager is not None:
            # found an item with that name, make sure it's a module(manager):
            if IModuleManager.isImplementedBy(manager):
                return manager.getModule()


        # See if out container is a RegistrationManagerContainer:
        c = self.__parent__
        if interfaces.IRegistrationManagerContainer.isImplementedBy(c):
            return c.findModule(name)

        # Use sys.modules in lieu of module service:
        module = sys.modules.get(name)
        if module is not None:
            return module

        raise ImportError(name)


    def resolve(self, name):
        l = name.rfind('.')
        mod = self.findModule(name[:l])
        return getattr(mod, name[l+1:])


class ComponentRegistrationAdapter(ObjectEntryAdapter):

    """Fssync adapter for ComponentRegistration objects and subclasses.

    This is fairly generic -- it should apply to most subclasses of
    ComponentRegistration.  But in order for it to work for a
    specific subclass (say, UtilityRegistration), you have to (a) add
    an entry to configure.zcml, like this:

        <fssync:adapter
            class=".utility.UtilityRegistration"
            factory=".registration.ComponentRegistrationAdapter"
            />

    and (b) add a function to factories.py, like this:

        def UtilityRegistration():
            from zope.app.services.utility import UtilityRegistration
            return UtilityRegistration("", None, "")

    The file representation of a registration object is an XML pickle
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



# XXX Pickle backward compatability
ConfigurationRegistry = RegistrationStack
ConfigurationManager = RegistrationManager
import sys
sys.modules['zope.app.services.registrationmanager'
            ] = sys.modules['zope.app.services.registration']
sys.modules['zope.app.services.configuration'
            ] = sys.modules['zope.app.services.registration']
