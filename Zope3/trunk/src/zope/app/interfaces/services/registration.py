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
"""Interfaces for objects supporting registration

$Id: registration.py,v 1.12 2003/10/16 19:38:42 fdrake Exp $
"""
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.annotation import IAnnotatable
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.container  import IContainerNamesContainer, IContainer
from zope.app.security.permission import PermissionField
from zope.interface import Interface, Attribute, implements
from zope.schema import TextLine
from zope.schema.interfaces import ITextLine

UnregisteredStatus = _('Unregistered')
RegisteredStatus = _('Registered')
ActiveStatus = _('Active')

class IRegistrationStatus(ITextLine):
    """The status of a registration
    """

class RegistrationStatus(TextLine):
    implements(IRegistrationStatus)

    def __init__(self, *args, **kw):
        super(RegistrationStatus, self).__init__(*args, **kw)
        self.allowed_values = (UnregisteredStatus,
                               RegisteredStatus,
                               ActiveStatus)

class INoLocalServiceError(Interface):
    """No local service to register with.
    """

class NoLocalServiceError(Exception):
    """No local service to configure

    An attempt was made to register a registration for which there is
    no local service.
    """

    implements(INoLocalServiceError)

class IRegistration(Interface):
    """Registration object

    A registration object represents a specific registration
    decision, such as registering an adapter or defining a permission.

    In addition to the attributes or methods defined here,
    registration objects will include additional attributes
    identifying how they should be used. For example, a service
    registration will provide a service type. An adapter
    registration will specify a used-for interface and a provided
    interface.
    """

    serviceType = Attribute("service type that manages "
                            "this registration type")
    # A string; typically a class attribute

    status = RegistrationStatus(
        title=_("Registration status")
        )

    def activated():
        """Method called when a registration is made active.
        """

    def deactivated():
        """Method called when a registration is made inactive.
        """

    def usageSummary():
        """Single-line usage summary.

        This should include the registrayion keys and the kind of
        registration. For example, a service registration will have a
        usage summary that indicates a registration for a service of
        some type.  (e.g. "View Service")

        """

    def implementationSummary():
        """Single-line implementation summary.

        This summarizes about the implementation of the thing being
        registered. For example, for local-component registrations,
        this will include the component path. For a page registration,
        this might include a template path and a dotted class name.
        """


class INamedRegistration(IRegistration):
    """Registration object that is registered only by name.
    """

    name = TextLine(
        title=_("Name"),
        description=_("The name that is registered"),
        readonly=True,
        # Don't allow empty or missing name:
        required=True,
        min_length=1,
        )

    # The label is generally set as a class attribute on the
    # registration class.
    label = Attribute("Descriptive label of the registration type "
                      "(for example, Service, Connection)")


class IComponentPath(ITextLine):
    """A component path
    """
    # This is juse the interface for the ComponentPath field below.
    # We'll use this as the basis for looking up an appriate widget.

class ComponentPath(TextLine):
    """A component path

    Values of the field are absolute unicode path strings that can be
    traversed to get an object.
    """
    implements(IComponentPath)


class IComponentRegistration(IRegistration):
    """Registration object that uses a component path and a permission."""

    componentPath = ComponentPath(
        title=_("Component path"),
        description=_("The path to the component; this may be absolute, "
                      "or relative to the nearest site management folder"),
        required=True)

    permission = PermissionField(
        title=_("The permission needed to use the component"),
        required=False,
        )

    def getComponent():
        """Return the component named in the registration.
        """


class INamedComponentRegistration(INamedRegistration,
                                  IComponentRegistration):
    """Components registered by name, using componemt path and permission."""


class IRegistrationStack(Interface):
    """A stack of registrations for a set of parameters

    A service will have a registry containing registry stacks
    for specific parameters.  For example, an adapter service will
    have a registry stack for each given used-for and provided
    interface.

    The registry stack works like a stack: the first element is
    active; when it is removed, the element after it is automatically
    activated.  An explicit None may be present (at most once) to
    signal that nothing is active.  To deactivate an element, it is
    moved to the end.
    """

    def register(registration):
        """Register the given registration without activating it.

        Do nothing if the registration is already registered.
        """

    def unregister(registration):
        """Unregister the given registration.

        Do nothing if the registration is not registered.

        Implies deactivate() if the registration is active.
        """

    def registered(registration):
        """Is the registration registered?

        Return a boolean indicating whether the registration has been
        registered.
        """

    def activate(registration):
        """Make the registration active.

        The activated() method is called on the registration.  If
        another registration was previously active, its deactivated()
        method is called first.

        If the argument is None, the currently active registration if
        any is disabled and no new registration is activated.

        Raises a ValueError if the given registration is not registered.
        """

    def deactivate(registration):
        """Make the registration inactive.

        If the registration is active, the deactivated() method is
        called on the registration.  If this reveals a registration
        that was previously active, that registration's activated()
        method is called.

        Raises a ValueError if the given registration is not registered.

        The call has no effect if the registration is registered but
        not active.
        """

    def active():
        """Return the active registration, if any.

        Otherwise, returns None.
        """

    def info(keep_dummy=False):
        """Return a sequence of registration information.

        The sequence items are mapping objects with keys:

        id -- A string that can be used to uniquely identify the
              registration.

        active -- A boolean indicating whether the registration is
                  active.

        registration -- The registration object.

        If keep_dummy is true, an entry corresponding to the dummy
        entry's position is returned whose value is
        {id: '',
         active: (True iff it is the first entry),
         registration: None}.
        """

    def __nonzero__(self):
        """The registry is true iff it has no registrations."""


class IRegistry(Interface):
    """A component that can be configured using a registration manager."""

    def queryRegistrationsFor(registration, default=None):
        """Return an IRegistrationStack for the registration.

        Data on the registration is used to decide which registry to
        return. For example, a service manager will use the
        registration name attribute to decide which registry
        to return.

        Typically, an object that implements this method will also
        implement a method named queryRegistrations, which takes
        arguments for each of the parameters needed to specify a set
        of registrations.

        The registry must be in the context of the registry.

        """

    def createRegistrationsFor(registration):
        """Create and return an IRegistrationStack for the registration.

        Data on the registration is used to decide which regsitry to
        create. For example, a service manager will use the
        registration name attribute to decide which regsitry
        to create.

        Typically, an object that implements this method will also
        implement a method named createRegistrations, which takes
        arguments for each of the parameters needed to specify a set
        of registrations.

        Calling createRegistrationsFor twice for the same registration
        returns the same registry.

        The registry must be in the context of the registry.

        """


class INameRegistry(IRegistry):
    """An IRegistry, where a name is used to decide which registry to
    return for methods in IRegistry.

    All registrations that pass through queryRegistrationsFor and
    createRegistrationsFor are expected to implement INamedRegistration.
    """

    def queryRegistrations(name, default=None):
        """Return an IRegistrationRegistry for the registration name.

        queryRegistrationsFor(cfg, default) is equivalent to
        queryRegistrations(cfg.name, default)
        """

    def createRegistrationsFor(registration):
        """Create and return an IRegistrationRegistry for the registration
        name.

        createRegistrationsFor(cfg, default) is equivalent to
        createRegistrations(cfg.name, default)
        """

    def listRegistrationNames():
        """Return a list of all registered registration names.
        """

class INameComponentRegistry(INameRegistry):
    """An INameRegistry where the registrations refer to components.

    All registrations that pass through queryRegistrationsFor and
    createRegistrationsFor are expected to implement
    INamedComponentRegistration.
    """
    def queryActiveComponent(name, default=None):
        """Finds the registration registry for a given name, checks if it has
        an active registration, and if so, returns its component.  Otherwise
        returns default.
        """

class IRegisterable(IAnnotatable):
    """A marker interface."""

class IRegistered(IRegisterable):
    """An object that can keep track of its configured uses.

    The object need not implement this functionality itself, but must at
    least support doing so via an adapter.
    """

    def addUsage(location):
        """Add a usage by location.

        The location is the physical path to the registration object that
        configures the usage.
        """
    def removeUsage(location):
        """Remove a usage by location.

        The location is the physical path to the registration object that
        configures the usage.
        """
    def usages():
        """Return a sequence of locations.

        A location is a physical path to a registration object that
        configures a usage.
        """

    def registrations():
        """Return a sequence of registration objects for this object."""

class IAttributeRegisterable(IAttributeAnnotatable, IRegisterable):
    """A marker interface."""


class IOrderedContainer(Interface):
    """Containers whose items can be reorderd.

    XXX This is likely to go.
    """

    def moveTop(names):
        """Move the objects corresponding to the given names to the top.
        """

    def moveUp(names):
        """Move the objects corresponding to the given names up.
        """

    def moveBottom(names):
        """Move the objects corresponding to the given names to the bottom.
        """

    def moveDown(names):
        """Move the objects corresponding to the given names down.
        """

class IRegistrationManager(IContainerNamesContainer, IOrderedContainer):
    """Manage Registrations
    """

    def addRegistration(registration):
        """Add a registration

        The registration name is chosen automatically. The chosen name
        is returned.
        """


class INoRegistrationManagerError(Interface):
    """No registration manager error
    """

class NoRegistrationManagerError(Exception):
    """No registration manager

    There is no registration manager in a site-management folder, or
    an operation would result in no registration manager in a
    site-management folder.

    """
    implements(INoRegistrationManagerError)

class IRegistrationManagerContainer(IContainer):
    """Containers with registration managers

    These are site-management folders of one sort or another.

    The container allows clients to access the registration manager
    without knowing it's name.

    XXX at this point, it doesn't really make sense for regsitration
    managers to be items.  It would probably be better to expose the
    registrations as a separate tab.

    The container prevents deletion of the last registration manager.

    The container may allow more than one registration manager. If it
    has more than one, the one returned from an unnamed access is
    undefined. XXX the container should allow one and only one.

    The registration manager container *also* supports local-module
    lookup.

    """

    def getRegistrationManager():
        """get a registration manager.

        Find a registration manager.  Clients can get the
        registration manager without knowing it's name. Normally,
        folders have one registration manager. If there is more than
        one, this method willl return one; which one is undefined.

        An error is raised if no registration manager can be found.
        """

    def findModule(name):
        """Find the module of the given name.

        If the module can be find in the folder or a parent folder
        (within the site manager), then return it, otherwise, delegate
        to the module service.

        This must return None when the module is not found.

        """

    def resolve(name):
        """Resolve a dotted object name.

        A dotted object name is a dotted module name and an object
        name within the module.

        XXX We really should switch to using some other character than
        a dot for the delimiter between the module and the object
        name.

        """



# XXX Pickle backward compatability
IUseConfigurable = IRegisterable
import sys
sys.modules['zope.app.interfaces.services.configuration'
            ] = sys.modules['zope.app.interfaces.services.registration']
