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
"""Component and Component Architecture Interfaces

$Id: interfaces.py,v 1.21 2004/03/02 14:26:16 srichter Exp $
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
        service definitions above them, but this can be overridden"""

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
        the specified interface.  If one is not found, returns default."""

    def getUtilitiesFor(context, interface):
        """Look up the registered utilities that provide an interface.

        Returns the list of utilities found

        """
        
    # Adapter service

    def getAdapter(object, interface, context=None):
        """Get an adapter to an interface for an object

        Returns the nearest adapter to the context that can adapt
        object to interface.  If context is not specified, attempts to
        use wrapping around object to specify a context.  If a
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
        use wrapping around object to specify a context.  If a
        matching adapter cannot be found, raises ComponentLookupError.

        The name consisting of an empty string is reserved for unnamed
        adapters. The unnamed adapter methods will often call the
        named adapter methods with an empty string for a name.

        """

    def queryAdapter(object, interface, default=None, context=None):
        """Look for an adapter to an interface for an object

        Returns the nearest adapter to the context that can adapt
        object to interface.  If context is not specified, attempts to
        use wrapping around object to specify a context.  If a matching
        adapter cannot be found, returns the default.

        If the object has a __conform__ method, this method will be
        called with the requested interface.  If the method returns a
        non-None value, that value will be returned. Otherwise, if the
        object already implements the interface, the object will be
        returned.

        """

    def queryNamedAdapter(object, interface, name, default=None, context=None):
        """Look for a named adapter to an interface for an object

        Returns the nearest named adapter to the context that can adapt
        object to interface.  If context is not specified, attempts to
        use wrapping around object to specify a context.  If a matching
        adapter cannot be found, returns the default.

        The name consisting of an empty string is reserved for unnamed
        adapters. The unnamed adapter methods will often call the
        named adapter methods with an empty string for a name.

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

    def getFactory(context, name):
        """Get a factory

        Get the factory of the given name that is nearest to the
        context.  If a matching factory cannot be found raises
        ComponentLookupError

        """

    def queryFactory(context, name, default=None):
        """Get a factory

        Get the factory of the given name that is nearest to the
        context.  If a matching factory cannot be found then the
        default is returned.

        """

    def getFactoryInterfaces(context, name):
        """Get interfaces implemented by a factory

        finds the factory of the given name that is nearest to the
        context, and returns the interface or interface tuple that
        object instances created by the named factory will implement."""

    # Presentation service

    def getView(object, name, request, context=None,
                providing=Interface):
        """Get a named view for a given object.

        The request must implement IPresentationRequest: it provides
        the view type and the skin name.  The nearest one to the
        object is found. If a matching view cannot be found, raises
        ComponentLookupError.

        If context is not specified, attempts to use wrapping around
        object to specify a context.

        """

    def queryView(object, name, request,
                  default=None, context=None, providing=Interface):
        """Look for a named view for a given object.

        The request must implement IPresentationRequest: it provides the view
        type and the skin name.  The nearest one to the object is
        found. If a matching view cannot be found, returns default.

        If context is not specified, attempts to use wrapping around
        object to specify a context.

        """

    def getDefaultViewName(object, request, context=None):
        """Get the name of the default view for the object and request.

        The request must implement IPresentationRequest, and provides the
        desired view type.  The nearest one to the object is found.
        If a matching default view name cannot be found, raises
        NotFoundError.

        If context is not specified, attempts to use wrapping around
        object to specify a context.

        """

    def queryDefaultViewName(object, request, default=None, context=None):
        """Look for the name of the default view for the object and request.

        The request must implement IPresentationRequest, and provides the
        desired view type.  The nearest one to the object is found.
        If a matching default view name cannot be found, returns the
        default.

        If context is not specified, attempts to use wrapping around
        object to specify a context.

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

    # XXX Because __call__ does not receive a context, it is not possible
    #     to write a factory that does its job in terms of another factory.
    #     This functionality is needed for making advanced factories that
    #     do what other factories do, and then mark the resultant object
    #     with an interface.
    def __call__(*args, **kw):
        """Return an instance of the objects we're a factory for."""


    def getInterfaces():
        """Get the interfaces implemented by the factory

        Return the interface(s) that objects created by this factory
        will implement.
        """

class IFactoryInfo(Interface):
    """Additional information about a factory."""

    title = Attribute("The factory title.")

    description = Attribute("A brief description of the factory.")


class IFactoryService(Interface):
    """A service to manage Factories."""

    def createObject(name, *args, **kwargs):
        """Create an object using a factory

        Create a new object using the factory with the given name,
        passing all remaining arguments to the factory transparently.

        A ComponentLookupError will be raised if the factory component
        can't be found.
        """

    def getFactory(name):
        """Return a registered factory

        A ComponentLookupError will be
        raised if the factory component can't be found.
        """

    def queryFactory(name, default=None):
        """Return a registered factory
        """

    def getInterfaces(name):
        """returns the interface or interface tuple that
        object instances created by the named factory will implement."""

    def getFactoriesFor(iface):
        """Return a tuple (name, factory) of registered factories that
        create objects which implement the given interface.

        A ComponentLookupError will be  raised if the factory component
        can't be found.
        """

    def queryFactoriesFor(iface, default=None):
        """Return a tuple (name, factory) list of registered factories
        that create objects which implement the given interface

        If no factory is found, the default value is returned.
        """

    def getFactoryInfo(name):
        """Returns information about the specified factory.

        Return value implements IFactoryInfo or is None if information
        about the factory is not available.
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

        If none is found, return an empty list
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

    def getRegisteredMatching(required=None, provided=None,
                              name=None, with=None):
        """Return information about registered data

        Zero or more for and provided interfaces may be
        specified. Registration information matching any of the
        specified interfaces is returned.

        The arguments may be interfaces, or sequences of interfaces.

        The returned value is a sequence of three-element tuples:

        - required interface

        - provided interface

        - the object registered specifically for the required and
          provided interfaces.
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
    """An IPresentationRequest provides methods for getting view meta data.
    """

    def getPresentationSkin():
        """Get the skin to be used for a request.

        The skin is a string as would be passed
        to IViewService.getView.
        """

class IResource(IPresentation):
    """Resources provide data to be used for presentation.
    """

class IResourceFactory(Interface):
    """A factory to create factories using the request."""

    def __call__(request):
        """Create a resource for a request

        The request must be an IPresentationRequest.

        """

class IView(IPresentation, IContextDependent):
    """Views provide a connection between an external actor and an object
    """

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

    def queryMultiView(objects, name, request, providing=Interface,
                       default=None):
        """Adapt the given objects and request

        The first argument is a tuple of objects to be adapted with the
        request.
        """
