############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
"""Component and Component Architecture Interfaces

$Id$
"""
from zope.interface import Interface, Attribute
from zope.exceptions import NotFoundError

# BBB: Backward-compatibility; 12/05/2004
from bbb.interfaces import *


class ComponentLookupError(NotFoundError):
    """A component could not be found."""

class Invalid(Exception):
    """A component doesn't satisfy a promise."""

class Misused(Exception):
    """A component is being used (registered) for the wrong interface."""


class IComponentArchitecture(Interface, IBBBComponentArchitecture):
    """The Component Architecture is defined by two key components: Adapters
    and Utiltities. Both are managed by site managers. All other components
    build on top of them.
    """

    # Utility API

    def getUtility(interface, name='', context=None):
        """Get the utility that provides interface

        Returns the nearest utility to the context that implements the
        specified interface.  If one is not found, raises
        ComponentLookupError.
        """

    def queryUtility(interface, name='', default=None, context=None):
        """Look for the utility that provides interface

        Returns the nearest utility to the context that implements
        the specified interface.  If one is not found, returns default.
        """

    def getUtilitiesFor(interface, context=None):
        """Return the utilities that provide an interface

        An iterable of utility name-value pairs is returned.
        """

    def getAllUtilitiesRegisteredFor(interface, context=None):
        """Return all registered utilities for an interface

        This includes overridden utilities.

        An iterable of utility instances is returned.  No names are
        returned.
        """

    # Adapter API

    def getAdapter(object, interface, name, context=''):
        """Get a named adapter to an interface for an object

        Returns an adapter that can adapt object to interface.  If a matching
        adapter cannot be found, raises ComponentLookupError.

        If context is None, an application-defined policy is used to choose
        an appropriate service manager from which to get an 'Adapters' service.

        If 'context' is not None, context is adapted to IServiceService,
        and this adapter's 'Adapters' service is used.
        """

    def getAdapterInContext(object, interface, context):
        """Get a special adapter to an interface for an object

        NOTE: This method should only be used if a custom context
        needs to be provided to provide custom component
        lookup. Otherwise, call the interface, as in::

           interface(object)

        Returns an adapter that can adapt object to interface.  If a matching
        adapter cannot be found, raises ComponentLookupError.

        Context is adapted to IServiceService, and this adapter's
        'Adapters' service is used.

        If the object has a __conform__ method, this method will be
        called with the requested interface.  If the method returns a
        non-None value, that value will be returned. Otherwise, if the
        object already implements the interface, the object will be
        returned.
        """

    def getMultiAdapter(objects, interface, name='', context=None):
        """Look for a multi-adapter to an interface for an objects

        Returns a multi-adapter that can adapt objects to interface.  If a
        matching adapter cannot be found, raises ComponentLookupError.

        If context is None, an application-defined policy is used to choose
        an appropriate service manager from which to get an 'Adapters' service.

        If 'context' is not None, context is adapted to IServiceService,
        and this adapter's 'Adapters' service is used.

        The name consisting of an empty string is reserved for unnamed
        adapters. The unnamed adapter methods will often call the
        named adapter methods with an empty string for a name.
        """

    def queryAdapter(object, interface, name, default=None, context=None):
        """Look for a named adapter to an interface for an object

        Returns an adapter that can adapt object to interface.  If a matching
        adapter cannot be found, returns the default.

        If context is None, an application-defined policy is used to choose
        an appropriate service manager from which to get an 'Adapters' service.

        If 'context' is not None, context is adapted to IServiceService,
        and this adapter's 'Adapters' service is used.
        """

    def queryAdapterInContext(object, interface, context, default=None):
        """Look for a special adapter to an interface for an object

        NOTE: This method should only be used if a custom context
        needs to be provided to provide custom component
        lookup. Otherwise, call the interface, as in::

           interface(object, default)

        Returns an adapter that can adapt object to interface.  If a matching
        adapter cannot be found, returns the default.

        Context is adapted to IServiceService, and this adapter's
        'Adapters' service is used.

        If the object has a __conform__ method, this method will be
        called with the requested interface.  If the method returns a
        non-None value, that value will be returned. Otherwise, if the
        object already implements the interface, the object will be
        returned.
        """

    def queryMultiAdapter(objects, interface, name='', default=None,
                          context=None):
        """Look for a multi-adapter to an interface for objects

        Returns a multi-adapter that can adapt objects to interface.  If a
        matching adapter cannot be found, returns the default.

        If context is None, an application-defined policy is used to choose
        an appropriate service manager from which to get an 'Adapters' service.

        If 'context' is not None, context is adapted to IServiceService,
        and this adapter's 'Adapters' service is used.

        The name consisting of an empty string is reserved for unnamed
        adapters. The unnamed adapter methods will often call the
        named adapter methods with an empty string for a name.
        """

    def getAdapters(objects, provided, context=None):
        """Look for all matching adapters to a provided interface for objects

        Return a list of adapters that match. If an adapter is named, only the
        most specific adapter of a given name is returned.

        If context is None, an application-defined policy is used to choose
        an appropriate service manager from which to get an 'Adapters'
        service.

        If 'context' is not None, context is adapted to IServiceService,
        and this adapter's 'Adapters' service is used.
        """

    def subscribers(required, provided, context=None):
        """Get subscribers

        Subscribers are returned that provide the provided interface
        and that depend on and are computed from the sequence of
        required objects.

        If context is None, an application-defined policy is used to choose
        an appropriate service manager from which to get an 'Adapters'
        service.

        If 'context' is not None, context is adapted to IServiceService,
        and this adapter's 'Adapters' service is used.
        """


    # Factory service

    # TODO: Hard to make context a keyword, leaving as it is. Maybe we should
    #       at least move it to the second position.
    def createObject(context, name, *args, **kwargs):
        """Create an object using a factory

        Finds the factory of the given name that is nearest to the
        context, and passes the other given arguments to the factory
        to create a new instance. Returns a reference to the new
        object.  If a matching factory cannot be found raises
        ComponentLookupError
        """

    def getFactoryInterfaces(name, context=None):
        """Get interfaces implemented by a factory

        Finds the factory of the given name that is nearest to the
        context, and returns the interface or interface tuple that
        object instances created by the named factory will implement.
        """

    def getFactoriesFor(interface, context=None):
        """Return a tuple (name, factory) of registered factories that
        create objects which implement the given interface.
        """


class ISiteManager(Interface):
    """ """

    def queryAdapter(object, interface, name, default=None):
        """Look for a named adapter to an interface for an object

        If a matching adapter cannot be found, returns the default.

        The name consisting of an empty string is reserved for unnamed
        adapters. The unnamed adapter methods will often call the
        named adapter methods with an empty string for a name.
        """

    def queryMultiAdapter(objects, interface, name, default=None):
        """Look for a multi-adapter to an interface for an object

        If a matching adapter cannot be found, returns the default.

        The name consisting of an empty string is reserved for unnamed
        adapters. The unnamed adapter methods will often call the
        named adapter methods with an empty string for a name.
        """

    def getAdapters(objects, provided):
        """Look for all matching adapters to a provided interface for objects

        Return a list of adapters that match. If an adapter is named, only the
        most specific adapter of a given name is returned.
        """

    def subscribers(required, provided):
        """Get subscribers

        Subscribers are returned that provide the provided interface
        and that depend on and are comuted from the sequence of
        required objects.
        """

    def queryUtility(interface, name='', default=None):
        """Look up a utility that provides an interface.

        If one is not found, returns default.
        """

    def getUtilitiesFor(interface):
        """Look up the registered utilities that provide an interface.

        Returns an iterable of name-utility pairs.
        """

    def getAllUtilitiesRegisteredFor(interface):
        """Return all registered utilities for an interface

        This includes overwridden utilities.

        An iterable of utility instances is returned.  No names are
        returned.
        """



class IRegistry(Interface):
    """Object that supports component registry
    """

    def registrations():
        """Return an iterable of component registrations
        """

class IFactory(Interface):
    """A factory is responsible for creating other components."""

    title = Attribute("The factory title.")

    description = Attribute("A brief description of the factory.")

    def __call__(*args, **kw):
        """Return an instance of the objects we're a factory for."""


    def getInterfaces():
        """Get the interfaces implemented by the factory

        Return the interface(s), as an instance of Implements, that objects
        created by this factory will implement. If the callable's Implements
        instance cannot be created, an empty Implements instance is returned.
        """
