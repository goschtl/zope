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

$Id: registration.py,v 1.1 2003/06/21 21:22:12 jim Exp $
"""
__metaclass__ = type



from persistence import Persistent
from zope.interface import implements
from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.container import IAddNotifiable, IDeleteNotifiable
from zope.app.interfaces.container import IZopeWriteContainer
from zope.app.interfaces.dependable import IDependable, DependencyError

from zope.app.interfaces.services.registration import IRegistrationManager
from zope.app.interfaces.services.registration import IRegistrationStack
from zope.app.interfaces.services.registration \
     import INameComponentRegistry
from zope.app.interfaces.services.registration import INamedRegistration
from zope.app.interfaces.services.registration import IRegistration
from zope.app.interfaces.services.registration \
     import INamedComponentRegistration
from zope.app.interfaces.services.registration import INameRegistry
from zope.app.interfaces.services.registration \
     import INamedComponentRegistration, IComponentRegistration
from zope.app.interfaces.services.registration import IRegistered
from zope.app.interfaces.services.registration \
     import NoRegistrationManagerError
from zope.app.interfaces.services.registration import NoLocalServiceError

from zope.app.interfaces.services.registration import UnregisteredStatus
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.interfaces.services.registration import RegisteredStatus
from zope.app.traversing import getRoot, getPath, traverse
from zope.component import getAdapter, queryAdapter
from zope.component import getServiceManager
from zope.app.context import ContextWrapper
from zope.context import ContextMethod, ContextDescriptor, getWrapperContainer
from zope.proxy import removeAllProxies
from zope.security.checker import InterfaceChecker
from zope.security.proxy import Proxy, trustedRemoveSecurityProxy
from zope.proxy import getProxiedObject

class RegistrationStatusProperty(ContextDescriptor):

    def __get__(self, inst, klass):
        if inst is None:
            return self

        registration = inst

        sm = getServiceManager(registration)
        service = sm.queryLocalService(registration.serviceType)
        # XXX The following may fail; there's a subtle bug here when
        # the returned service isn't in the same service manager as
        # the one owning the registration.
        registry = service and service.queryRegistrationsFor(registration)

        if registry:

            if registry.active() == registration:
                return ActiveStatus
            if registry.registered(registration):
                return RegisteredStatus

        return UnregisteredStatus

    def __set__(self, inst, value):
        registration = inst

        sm = getServiceManager(registration)
        service = sm.queryLocalService(registration.serviceType)

        registry = service and service.queryRegistrationsFor(registration)

        if value == UnregisteredStatus:
            if registry:
                registry.unregister(registration)

        else:
            if not service:
                raise NoLocalServiceError(
                    "This registration change cannot be performed because "
                    "there isn't a corresponding %s service defined in this "
                    "site. To proceed, first add a local %s service."
                    % (registration.serviceType, registration.serviceType))

            if registry is None:
                registry = service.createRegistrationsFor(registration)

            if value == RegisteredStatus:
                if registry.active() == registration:
                    registry.deactivate(registration)
                else:
                    registry.register(registration)

            elif value == ActiveStatus:
                if not registry.registered(registration):
                    registry.register(registration)
                registry.activate(registration)


class RegistrationStack(Persistent):

    """Registration registry implementation.

    The invariants for _data are as follows:

        (1) The last element (if any) is not None

        (2) No value occurs more than once

        (3) Each value except None is a relative path from the nearest
            service manager to an object implementing IRegistration
    """

    implements(IRegistrationStack)

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
            raise ValueError("Registration object is in an invalid location",
                             path)

        rpath = path[lpackages+len(prefix):]
        if not rpath or (".." in rpath.split("/")):
            raise ValueError("Registration object is in an invalid location",
                             path)

        return rpath

    def register(wrapped_self, registration):
        cid = wrapped_self._id(registration)

        if wrapped_self._data:
            if cid in wrapped_self._data:
                return # already registered
        else:
            # Nothing registered. Need to stick None in front so that nothing
            # is active.
            wrapped_self._data = (None, )

        wrapped_self._data += (cid, )
    register = ContextMethod(register)

    def unregister(wrapped_self, registration):
        cid = wrapped_self._id(registration)

        data = wrapped_self._data
        if data:
            if data[0] == cid:
                # Tell it that it is no longer active
                registration.deactivated()

            # Remove it from our data
            data = tuple([item for item in data if item != cid])

            # Check for trailing None
            if data and data[-1] is None:
                data = data[:-1]

            if data and data[0] is not None:
                # Activate the newly active component
                sm = getServiceManager(wrapped_self)
                new = traverse(sm, data[0])
                new.activated()

            # Write data back
            wrapped_self._data = data
    unregister = ContextMethod(unregister)

    def registered(wrapped_self, registration):
        cid = wrapped_self._id(registration)
        return cid in wrapped_self._data
    registered = ContextMethod(registered)

    def activate(wrapped_self, registration):
        if registration is None:
            cid = None
        else:
            cid = wrapped_self._id(registration)
        data = wrapped_self._data

        if cid is None and not data:
            return # already in the state we want

        if cid is None or cid in data:

            if data[0] == cid:
                return # already active

            if data[0] is not None:
                # Deactivate the currently active component
                sm = getServiceManager(wrapped_self)
                old = traverse(sm, data[0])
                old.deactivated()

            # Insert it in front, removing it from back
            data = (cid, ) + tuple([item for item in data if item != cid])

            # Check for trailing None
            if data[-1] == None:
                data = data[:-1]

            # Write data back
            wrapped_self._data = data

            if registration is not None:
                # Tell it that it is now active
                registration.activated()

        else:
            raise ValueError(
                "Registration to be activated is not registered",
                registration)
    activate = ContextMethod(activate)

    def deactivate(wrapped_self, registration):
        cid = wrapped_self._id(registration)
        data = wrapped_self._data

        if cid not in data:
            raise ValueError(
                "Registration to be deactivated is not registered",
                registration)

        if data[0] != cid:
            return # already inactive

        # Tell it that it is no longer active
        registration.deactivated()

        if None not in data:
            # Append None
            data += (None,)

        # Move it to the end
        data = data[1:] + data[:1]

        if data[0] is not None:
            # Activate the newly active component
            sm = getServiceManager(wrapped_self)
            new = traverse(sm, data[0])
            new.activated()

        # Write data back
        wrapped_self._data = data
    deactivate = ContextMethod(deactivate)

    def active(wrapped_self):
        if wrapped_self._data:
            path = wrapped_self._data[0]
            if path is not None:
                # Make sure we can traverse to it.
                sm = getServiceManager(wrapped_self)
                registration = traverse(sm, path)
                return registration

        return None
    active = ContextMethod(active)

    def __nonzero__(self):
        return bool(self._data)

    def info(wrapped_self, keep_dummy=False):
        sm = getServiceManager(wrapped_self)

        data = wrapped_self._data
        if not data and keep_dummy:
            data += (None,)

        result = [{'id': path or "",
                   'active': False,
                   'registration': (path and traverse(sm, path))
                  }
                  for path in data if path or keep_dummy
                 ]

        if keep_dummy or (result and result[0]['registration'] is not None):
            result[0]['active'] = True

        return result
    info = ContextMethod(info)


class SimpleRegistration(Persistent):
    """Registration objects that just contain registration data

    Classes that derive from this must make sure they implement
    IDeleteNotifiable either by implementing
    implementedBy(SimpleRegistration) or explicitly implementing
    IDeleteNotifiable.
    """

    implements(IRegistration, IDeleteNotifiable,
                      # We are including this here because we want all of the
                      # subclasses to get it and we don't really need to be
                      # flexible about the policy here. At least we don't
                      # *think* we do. :)
                      IAttributeAnnotatable,
                      )

    # Methods from IRegistration

    def activated(self):
        pass

    def deactivated(self):
        pass

    def usageSummary(self):
        return self.__class__.__name__

    def implementationSummary(self):
        return ""

    # Methods from IDeleteNotifiable

    def beforeDeleteHook(self, registration, container):
        "See IDeleteNotifiable"

        objectstatus = registration.status

        if objectstatus == ActiveStatus:
            try:
                objectpath = getPath(registration)
            except: # XXX
                objectpath = str(registration)
            raise DependencyError("Can't delete active registration (%s)"
                                  % objectpath)
        elif objectstatus == RegisteredStatus:
            registration.status = UnregisteredStatus


class NamedRegistration(SimpleRegistration):
    """Named registration
    """

    implements(INamedRegistration)

    def __init__(self, name):
        self.name = name

    def usageSummary(self):
        return "%s %s" % (self.name, self.__class__.__name__)


class ComponentRegistration(SimpleRegistration):
    """Component registration.

    Subclasses should define a getInterface() method returning the interface
    of the component.
    """

    # SimpleRegistration implements IDeleteNotifiable, so we don't need
    # it below.
    implements(IComponentRegistration, IAddNotifiable)

    def __init__(self, component_path, permission=None):
        self.componentPath = component_path
        if permission == 'zope.Public':
            permission = CheckerPublic
        self.permission = permission

    def implementationSummary(self):
        return self.componentPath

    def getComponent(wrapped_self):
        service_manager = getServiceManager(wrapped_self)

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

    def afterAddHook(self, registration, container):
        "See IAddNotifiable"
        component = registration.getComponent()
        dependents = getAdapter(component, IDependable)
        objectpath = getPath(registration)
        dependents.addDependent(objectpath)
        # Also update usage, if supported
        adapter = queryAdapter(component, IRegistered)
        if adapter is not None:
            adapter.addUsage(getPath(registration))

    def beforeDeleteHook(self, registration, container):
        "See IDeleteNotifiable"
        super(ComponentRegistration, self).beforeDeleteHook(registration,
                                                             container)
        component = registration.getComponent()
        dependents = getAdapter(component, IDependable)
        objectpath = getPath(registration)
        dependents.removeDependent(objectpath)
        # Also update usage, if supported
        adapter = queryAdapter(component, IRegistered)
        if adapter is not None:
            adapter.removeUsage(getPath(registration))

class NamedComponentRegistration(NamedRegistration, ComponentRegistration):
    """Registrations for named components.

    This configures components that live in folders, by name.
    """
    implements(INamedComponentRegistration)

    def __init__(self, name, component_path, permission=None):
        NamedRegistration.__init__(self, name)
        ComponentRegistration.__init__(self, component_path, permission)


class NameRegistry:
    """Mixin for implementing INameRegistry
    """
    implements(INameRegistry)

    def __init__(self, *args, **kw):
        self._bindings = {}
        super(NameRegistry, self).__init__(*args, **kw)

    def queryRegistrationsFor(wrapped_self, cfg, default=None):
        """See IRegistry"""
        return wrapped_self.queryRegistrations(cfg.name, default)
    queryRegistrationsFor = ContextMethod(queryRegistrationsFor)

    def queryRegistrations(wrapped_self, name, default=None):
        """See INameRegistry"""
        registry = wrapped_self._bindings.get(name, default)
        return ContextWrapper(registry, wrapped_self)
    queryRegistrations = ContextMethod(queryRegistrations)

    def createRegistrationsFor(wrapped_self, cfg):
        """See IRegistry"""
        return wrapped_self.createRegistrations(cfg.name)
    createRegistrationsFor = ContextMethod(createRegistrationsFor)

    def createRegistrations(wrapped_self, name):
        """See INameRegistry"""
        try:
            registry = wrapped_self._bindings[name]
        except KeyError:
            wrapped_self._bindings[name] = registry = RegistrationStack()
            wrapped_self._p_changed = 1
        return ContextWrapper(registry, wrapped_self)
    createRegistrations = ContextMethod(createRegistrations)

    def listRegistrationNames(wrapped_self):
        """See INameRegistry"""
        return filter(wrapped_self._bindings.get,
                      wrapped_self._bindings.keys())


class NameComponentRegistry(NameRegistry):
    """Mixin for implementing INameComponentRegistry
    """
    implements(INameComponentRegistry)

    def queryActiveComponent(wrapped_self, name, default=None):
        """See INameComponentRegistry"""
        registry = wrapped_self.queryRegistrations(name)
        if registry:
            registration = registry.active()
            if registration is not None:
                return registration.getComponent()
        return default
    queryActiveComponent = ContextMethod(queryActiveComponent)


from zope.app.dependable import PathSetAnnotation

class Registered(PathSetAnnotation):
    """An adapter from IRegisterable to IRegistered.

    This class is the only place that knows how 'Registered'
    data is represented.
    """

    implements(IRegistered)

    # We want to use this key:
    #   key = "zope.app.services.registration.Registered"
    # But we have existing annotations with the following key, so we'll keep
    # it. :( 
    key = "zope.app.services.configuration.UseConfiguration"

    addUsage = PathSetAnnotation.addPath
    removeUsage = PathSetAnnotation.removePath
    usages = PathSetAnnotation.getPaths


class RegistrationManager(Persistent):
    """Registration manager

    Manages registrations within a package.
    """

    implements(IRegistrationManager, IDeleteNotifiable)

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


class RegistrationManagerContainer(object):
    """Mix-in to implement IRegistrationManagerContainer
    """

    def __init__(self):
        super(RegistrationManagerContainer, self).__init__()
        self.setObject('RegistrationManager', RegistrationManager())

    def __delitem__(self, name):
        """Delete an item, but not if it's the last registration manager
        """
        item = self[name]
        if IRegistrationManager.isImplementedBy(item):
            # Check to make sure it's not the last one
            if len([i for i in self.values()
                    if IRegistrationManager.isImplementedBy(i)]) < 2:
                raise NoRegistrationManagerError(
                    "Can't delete the last registration manager")
        super(RegistrationManagerContainer, self).__delitem__(name)

    def getRegistrationManager(self):
        """Get a registration manager
        """
        # Get the registration manager for this folder
        for name in self:
            item = self[name]
            if IRegistrationManager.isImplementedBy(item):
                # We found one. Get it in context
                return ContextWrapper(item, self, name=name)
        else:
            raise NoRegistrationManagerError(
                "Couldn't find an registration manager")
    getRegistrationManager = ContextMethod(getRegistrationManager)


from zope.xmlpickle import dumps, loads
from zope.app.interfaces.fssync import IObjectFile
from zope.app.fssync.classes import ObjectEntryAdapter

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
