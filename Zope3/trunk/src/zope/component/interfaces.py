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
"""

$Id: interfaces.py,v 1.3 2003/01/10 18:44:23 stevea Exp $
"""

from zope.interface import Interface, Attribute

class IComponentArchitecture(Interface):
    """The Component Architecture is defined by six key services,
    all of which are managed by service managers.
    """

    # basic service manager tools

    def getServiceManager(context):
        """returns the nearest service manager to the context; if the
        context is None the global service manager is always returned"""

    def getService(context, name):
        """returns the service defined by 'name' nearest to the context;
        if the context is None the pertinent global service is always
        returned"""

    def getServiceDefinitions(context):
        """returns a dictionary of the service definitions pertinent to
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

    # Adapter service

    def getAdapter(object, interface, name='', context=None):
        """Get adapter to interface for object

        Returns the nearest adapter to the context that can adapt
        object to interface.  If context is not specified, attempts to
        use wrapping around object to specify a context.  If a
        matching adapter cannot be found, raises ComponentLookupError.

        """

    def queryAdapter(object, interface, default=None, name='', context=None):
        """Look for adapter to interface for object

        Returns the nearest adapter to the context that can adapt
        object to interface.  If context is not specified, attempts to
        use wrapping around object to specify a context.  If a matching
        adapter cannot be found, returns default."""

    # Factory service

    def createObject(context, name, *args, **kwargs):
        """Create an object using a factory

        finds the factory of the given name that is nearest to the
        context, and passes the other given arguments to the factory
        to create a new instance. Returns a reference to the new
        object.  If a matching factory cannot be found raises
        ComponentLookupError

        """

    def getFactoryInterfaces(context, name):
        """finds the factory of the given name that is nearest to the
        context, and returns the interface or interface tuple that
        object instances created by the named factory will implement."""

    # Skin service

    def getSkin(wrapped_object, name, view_type):
        """Get a skin definition as a sequence of layers

        Returns the nearest skin (sequence of layer names) to the
        object, as specified by the name and the view type (browser,
        xml-rpc, etc.) as expressed by an interface.  If a matching
        skin is not found, raises ComponentLookupError

        There is a predefined skin in the global skin service, '', with
        a single layer, ''."""

    # View service

    def getView(wrapped_object, name, request):
        """Get a named view for a given object.

        The request must implement IPresentationRequest: it provides
        the view type and the skin name.  The nearest one to the
        object is found. If a matching view cannot be found, raises
        ComponentLookupError.

        """

    def queryView(wrapped_object, name, request, default=None):
        """Look for a named view for a given object.

        The request must implement IPresentationRequest: it provides the view
        type and the skin name.  The nearest one to the object is
        found. If a matching view cannot be found, returns default.

        """

    def getDefaultViewName(wrapped_object, request):
        """Get the name of the default view for the object and request.

        The request must implement IPresentationRequest, and provides the
        desired view type.  The nearest one to the object is found.
        If a matching default view name cannot be found, raises
        NotFoundError.

        """

    def queryDefaultViewName(wrapped_object, request, default=None):
        """Look for the name of the default view for the object and request.

        The request must implement IPresentationRequest, and provides the
        desired view type.  The nearest one to the object is found.
        If a matching default view name cannot be found, returns the
        default.

        """

    # Resource service

    def getResource(wrapped_object, name, request):
        """Get a named resource for a given request

        The request must implement IPresentationRequest.

        The object provides a place to look for placeful resources.

        A ComponentLookupError will be raised if the component can't
        be found.

        """

    def queryResource(wrapped_object, name, request, default=None):
        """Get a named resource for a given request

        The request must implement IPresentationRequest.

        The object provides a place to look for placeful resources.

        If the component can't be found, the default is returned.
        """

class IServiceService(Interface):

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

    def __call__():
        """Return an instance of the objects we're a factory for."""


    def getInterfaces():
        """Return the interface(s) that objects created by this factory
        will implement."""

class IFactoryService(Interface):

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


class IUtilityService(Interface):

    def getUtility(interface, name=''):
        """Look up a utility that provides an interface.

        If one is not found, raises ComponentLookupError.

        """

    def queryUtility(interface, default=None, name=''):
        """Look up a utility that provides an interface.

        If one is not found, returns default.

        """


class IContextDependent(Interface):

    context = Attribute(
        """The context of the object

        This is the object being adapted, viewed, extended, etc.

        """)

class IAdapterService(Interface):

    def getAdapter(object, interface, name=''):
        """Look up an adapter that provides an interface for an object

        If name is empty and the object already implements the
        interface, then the object will be returned.

        A ComponentLookupError will be
        raised if the component can't be found.
        """

    def queryAdapter(object, interface, default=None, name=''):
        """Look up an adapter that provides an interface for an object

        If name is empty and the object already implements the
        interface, then the object will be returned.

        The default will be returned if the component can't be found.
        """

    # XXX need to add name support
    def getRegisteredMatching(for_interfaces=None, provided_interfaces=None):
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

    def getPresentationType():
        """Get a view type

        The view type is expressed as an interface, as would be passed
        to IViewService.getView.
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

    def __call__(request):
        """Create a resource for a request

        The request must be an IPresentationRequest.

        """

class IResourceService(Interface):

    def getResource(object, name, request):
        """Look up a named resource for a given request

        The request must implement IPresentationRequest.

        The object provides a place to look for placeful resources.

        A ComponentLookupError will be
        raised if the component can't be found.
        """

    def queryResource(object, name, request, default=None):
        """Look up a named resource for a given request

        The request must implement IPresentationRequest.

        The object provides a place to look for placeful resources.

        The default will be returned if the component can't be found.
        """


class IView(IPresentation, IContextDependent):
    """Views provide a connection between an external actor and an object
    """

class IViewFactory(Interface):
    """Objects for creating views
    """

    def __call__(context, request):
        """Create an view (IView) object

        The context aregument is the object displayed by the view. The
        request argument is an object, such as a web request, that
        "stands in" for the user.
        """



class IViewService(Interface):

    def getView(object, name, request):
        """Get a named view for a given object and request

        The request must implement IPresentationRequest.

        The object also provides a place to look for placeful views.

        A ComponentLookupError will be
        raised if the component can't be found.
        """

    def queryView(object, name, request, default=None):
        """Look for a named view for a given object and request

        The request must implement IPresentationRequest.

        The object also provides a place to look for placeful views.

        The default will be returned
        if the component can't be found.
        """

    def getDefaultViewName(object, request):
        """Get the name of the default view for the object and request

        The request must implement IPresentationRequest.

        A NotFoundError will be raised if the suitable
        default view name for the object cannot be found.
        """

    def queryDefaultViewName(object, request, default=None):
        """Look for the name of the default view for the object and request

        The request must implement IPresentationRequest.

        The default will be returned if a suitable
        default view name for the object cannot be found.
        """

class ISkinService(Interface):

    def getSkin(object, name, view_type):
        """Return the sequence of layers (names) making up the skin.

        The object provides a place to look for placeful skin definitions.

        If the skin was not defined, an empty sequence will be returned.
        """
