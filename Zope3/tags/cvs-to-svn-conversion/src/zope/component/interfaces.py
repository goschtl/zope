############################################################################
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
############################################################################
"""Component and Component Architecture Interfaces

$Id: interfaces.py,v 1.34 2004/04/20 11:01:09 stevea Exp $
"""
from zope.interface import Interface, Attribute
from zope.component.exceptions import *

class IComponentArchitecture(Interface):
    """The Component Architecture is defined by six key services,
    all of which are managed by service managers.
    """

    # basic service manager tools

    def getServiceManager(context):
        """Get the service manager

        Return the nearest service manager to the context; if the
        context is None the global service manager is always returned
        """

    def getService(context, name):
        """Get a named service.

        Returns the service defined by 'name' nearest to the context;
        if the context is None the pertinent global service is always
        returned"""

    def getServiceDefinitions(context):
        """Get service definitions

        Returns a dictionary of the service definitions pertinent to
        the given context, in the format {nameString: serviceInterface}.
        If the context is None the global definitions will be returned.
        The default behavior of placeful service managers is to include
        service definitions above them, but this can be overridden.
        """

    # Utility service

    def getUtility(context, interface, name=''):
        """Get the utility that provides interface

        Returns the nearest utility to the context that implements the
        specified interface.  If one is not found, raises
        ComponentLookupError.
        """

    def queryUtility(context, interface, default=None, name=''):
        """Look for the utility that provides interface

        Returns the nearest utility to the context that implements
        the specified interface.  If one is not found, returns default.
        """

    def getUtilitiesFor(context, interface):
        """Return the utilitis that provide an interface

        An iterable of utility name-value pairs is returned.
        """
        
    # Adapter service

    def getAdapter(object, interface, context=None):
        """Get an adapter to an interface for an object

        Returns the nearest adapter to the context that can adapt
        object to interface.  If context is not specified, attempts to
        use  object to specify a context.  If a
        matching adapter cannot be found, raises ComponentLookupError.

        If the object has a __conform__ method, this method will be
        called with the requested interface.  If the method returns a
        non-None value, that value will be returned. Otherwise, if the
        object already implements the interface, the object will be
        returned.
        """

    def getNamedAdapter(object, interface, name, context=None):
        """Get a named adapter to an interface for an object

        Returns the nearest named adapter to the context that can adapt
        object to interface.  If context is not specified, attempts to
        use  object to specify a context.  If a
        matching adapter cannot be found, raises ComponentLookupError.

        The name consisting of an empty string is reserved for unnamed
        adapters. The unnamed adapter methods will often call the
        named adapter methods with an empty string for a name.
        """

    def getMultiAdapter(objects, interface, name='', context=None):
        """Look for a multi-adapter to an interface for an objects

        Returns the nearest multi-adapter to the context that can
        adapt objects to interface.  If context is not specified, the
        first object, if any, is used.  If a matching adapter cannot
        be found, raises ComponentLookupError.

        The name consisting of an empty string is reserved for unnamed
        adapters. The unnamed adapter methods will often call the
        named adapter methods with an empty string for a name.
        """

    def queryAdapter(object, interface, default=None, context=None):
        """Look for an adapter to an interface for an object

        Returns the nearest adapter to the context that can adapt
        object to interface.  If context is not specified, attempts to
        use  object to specify a context.  If a matching
        adapter cannot be found, returns the default.

        If the object has a __conform__ method, this method will be
        called with the requested interface.  If the method returns a
        non-None value, that value will be returned. Otherwise, if the
        object already implements the interface, the object will be
        returned.
        """

    def queryNamedAdapter(object, interface, name, default=None,
                          context=None):
        """Look for a named adapter to an interface for an object

        Returns the nearest named adapter to the context that can adapt
        object to interface.  If context is not specified, attempts to
        use  object to specify a context.  If a matching
        adapter cannot be found, returns the default.

        The name consisting of an empty string is reserved for unnamed
        adapters. The unnamed adapter methods will often call the
        named adapter methods with an empty string for a name.
        """

    def queryMultiAdapter(objects, interface, name='', default=None,
                          context=None):
        """Look for a multi-adapter to an interface for objects

        Returns the nearest multi-adapter to the context that can
        adapt objects to interface.  If context is not specified, the
        first object, if any, is used.  If a matching adapter cannot
        be found, returns the default.

        The name consisting of an empty string is reserved for unnamed
        adapters. The unnamed adapter methods will often call the
        named adapter methods with an empty string for a name.
        """

    def subscribers(required, provided, context=None):
        """Get subscribers

        Subscribers are returned that provide the provided interface
        and that depend on and are comuted from the sequence of
        required objects.

        Returns the subscribers for the context.  If context is not
        specified, attempts to use object to specify a context.
        """


    # Factory service

    def createObject(context, name, *args, **kwargs):
        """Create an object using a factory

        Finds the factory of the given name that is nearest to the
        context, and passes the other given arguments to the factory
        to create a new instance. Returns a reference to the new
        object.  If a matching factory cannot be found raises
        ComponentLookupError
        """

    def getFactoryInterfaces(context, name):
        """Get interfaces implemented by a factory

        finds the factory of the given name that is nearest to the
        context, and returns the interface or interface tuple that
        object instances created by the named factory will implement.
        """

    def getFactoriesFor(context, interface):
        """Return a tuple (name, factory) of registered factories that
        create objects which implement the given interface.
        """

    # XXX: This method is deprecated, since factories are utiltities
    def getFactory(context, name):
        """Get a factory

        Get the factory of the given name that is nearest to the
        context.  If a matching factory cannot be found raises
        ComponentLookupError
        """

    # XXX: This method is deprecated, since factories are utiltities
    def queryFactory(context, name, default=None):
        """Get a factory

        Get the factory of the given name that is nearest to the
        context.  If a matching factory cannot be found then the
        default is returned.
        """

    # Presentation service

    def getView(object, name, request, context=None,
                providing=Interface):
        """Get a named view for a given object.

        The request must implement IPresentationRequest: it provides
        the view type and the skin name.  The nearest one to the
        object is found. If a matching view cannot be found, raises
        ComponentLookupError.

        If context is not specified, attempts to use 
        object to specify a context.
        """

    def queryView(object, name, request,
                  default=None, context=None, providing=Interface):
        """Look for a named view for a given object.

        The request must implement IPresentationRequest: it provides
        the view type and the skin name.  The nearest one to the
        object is found.  If a matching view cannot be found, returns
        default.

        If context is not specified, attempts to use object to specify
        a context.
        """

    def getMultiView(objects, request, providing=Interface, name='',
                     context=None):
        """Look for a multi-view for given objects

        The request must implement IPresentationRequest: it provides
        the view type and the skin name.  The nearest one to the
        object is found.  If a matching view cannot be found, raises
        ComponentLookupError.

        If context is not specified, attempts to use the first object
        to specify a context.
        """

    def queryMultiView(objects, request, providing=Interface, name='',
                       default=None, context=None):
        """Look for a multi-view for given objects

        The request must implement IPresentationRequest: it provides
        the view type and the skin name.  The nearest one to the
        object is found.  If a matching view cannot be found, returns
        default.

        If context is not specified, attempts to use the first object
        to specify a context.
        """

    def getViewProviding(object, providing, request, context=None):
        """Look for a view based on the interface it provides.

        A call to this method is equivalent to:

            getView(object, '', request, context, providing)
        """

    def queryViewProviding(object, providing, request, 
                           default=None, context=None):
        """Look for a view that provides the specified interface.

        A call to this method is equivalent to:

            queryView(object, '', request, default, context, providing)
        """

    def getDefaultViewName(object, request, context=None):
        """Get the name of the default view for the object and request.

        The request must implement IPresentationRequest, and provides the
        desired view type.  The nearest one to the object is found.
        If a matching default view name cannot be found, raises
        NotFoundError.

        If context is not specified, attempts to use 
        object to specify a context.
        """

    def queryDefaultViewName(object, request, default=None, context=None):
        """Look for the name of the default view for the object and request.

        The request must implement IPresentationRequest, and provides
        the desired view type.  The nearest one to the object is
        found.  If a matching default view name cannot be found,
        returns the default.

        If context is not specified, attempts to use object to specify
        a context.
        """

    def getResource(wrapped_object, name, request, providing=Interface):
        """Get a named resource for a given request

        The request must implement IPresentationRequest.

        The object provides a place to look for placeful resources.

        A ComponentLookupError will be raised if the component can't
        be found.
        """

    def queryResource(wrapped_object, name, request,
                      default=None, providing=Interface):
        """Get a named resource for a given request

        The request must implement IPresentationRequest.

        The object provides a place to look for placeful resources.

        If the component can't be found, the default is returned.
        """

class IRegistry(Interface):
    """Object that supports component registry
    """

    def registrations():
        """Return an iterable of component registrations
        """

class IServiceService(Interface):
    """A service to manage Services."""

    def getServiceDefinitions():
        """Retrieve all Service Definitions

        Should return a list of tuples (name, interface)
        """

    def getInterfaceFor(name):
        """Retrieve the service interface for the given name
        """

    def getService(name):
        """Retrieve a service implementation

        Raises ComponentLookupError if the service can't be found.
        """

    def queryService(name, default=None):
        """Look for a named service.

        Return the default if the service can't be found.
        """

class IFactory(Interface):
    """A factory is responsible for creating other components."""

    title = Attribute("The factory title.")

    description = Attribute("A brief description of the factory.")

    # XXX Because __call__ does not receive a context, it is not possible
    #     to write a factory that does its job in terms of another factory.
    #     This functionality is needed for making advanced factories that
    #     do what other factories do, and then mark the resultant object
    #     with an interface.
    def __call__(*args, **kw):
        """Return an instance of the objects we're a factory for."""


    def getInterfaces():
        """Get the interfaces implemented by the factory

        Return the interface(s), as an instance of Implements, that objects
        created by this factory will implement. If the callable's Implements
        instance cannot be created, an empty Implements instance is returned.
        """


class IUtilityService(Interface):
    """A service to manage Utilities."""

    def getUtility(interface, name=''):
        """Look up a utility that provides an interface.

        If one is not found, raises ComponentLookupError.
        """

    def queryUtility(interface, default=None, name=''):
        """Look up a utility that provides an interface.

        If one is not found, returns default.
        """

    def getUtilitiesFor(interface):
        """Look up the registered utilities that provide an interface.

        Returns an iterable of name-utility pairs.
        """

class IContextDependent(Interface):
    """Components implementing this interface must have a context component.

    Usually the context must be one of the arguments of the
    constructor. Adapters and views are a primary example of context-dependent
    components.
    """

    context = Attribute(
        """The context of the object

        This is the object being adapted, viewed, extended, etc.
        """)

class IAdapterService(Interface):
    """A service to manage Adapters."""

    def queryAdapter(object, interface, default=None):
        """Look for an adapter to an interface for an object

        If a matching adapter cannot be found, returns the default.
        """

    def queryNamedAdapter(object, interface, name, default=None):
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

    def subscribers(required, provided):
        """Get subscribers

        Subscribers are returned that provide the provided interface
        and that depend on and are comuted from the sequence of
        required objects.
        """

class IPresentation(Interface):
    """Presentation components provide interfaces to external actors

    The are created for requests, which encapsulate external actors,
    connections, etc.
    """

    request = Attribute(
        """The request

        The request is a surrogate for the user. It also provides the
        presentation type and skin. It is of type
        IPresentationRequest.
        """)

class IPresentationRequest(Interface):
    """An IPresentationRequest provides methods for getting view meta data."""

    def getPresentationSkin():
        """Get the skin to be used for a request.

        The skin is a string as would be passed
        to IViewService.getView.
        """

class IResource(IPresentation):
    """Resources provide data to be used for presentation."""

class IResourceFactory(Interface):
    """A factory to create factories using the request."""

    def __call__(request):
        """Create a resource for a request

        The request must be an IPresentationRequest.
        """

class IView(IPresentation, IContextDependent):
    """Views provide a connection between an external actor and an object"""

class IViewFactory(Interface):
    """Objects for creating views"""

    def __call__(context, request):
        """Create an view (IView) object

        The context aregument is the object displayed by the view. The
        request argument is an object, such as a web request, that
        "stands in" for the user.
        """

class IPresentationService(Interface):
    """A service to manage Presentation components."""

    def queryResource(name, request, providing=Interface, default=None):
        """Look up a named resource for a given request

        The request must implement IPresentationRequest.

        The default will be returned if the component can't be found.
        """

    def queryView(object, name, request, providing=Interface, default=None):
        """Look for a named view for a given object and request

        The request must implement IPresentationRequest.

        The default will be returned if the component can't be found.
        """

    def queryMultiView(objects, request, providing=Interface, name='',
                       default=None):
        """Adapt the given objects and request

        The first argument is a tuple of objects to be adapted with the
        request.
        """
