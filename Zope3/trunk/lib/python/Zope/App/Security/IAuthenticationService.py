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

$Id: IAuthenticationService.py,v 1.4 2002/07/15 22:01:10 jim Exp $
"""

from Interface import Interface

class IAuthenticationService(Interface):
    """
    Provide support for establishing principals for requests and for
    performing protocol-specific actions, such as issuing challenges
    or providing login interfaces.
    
    IAuthenticationService objects are used to implement
    authentication services. Because they implement services, they are
    expected to collaborate with services in other contexts. Client
    code doesn't sarch a context and call multiple services. Instead,
    client code will call the most specific service in a place and
    rely on the service to delegate to other services as necessary.
    
    The interface doesn't include methods for data
    management. Services may use external data and not allow
    management in Zope. Simularly, the data to be managed may vary
    with different implementations of a service.
    """    

    def authenticate(request):
        """
        
        Indentify a principal for a request

        If a principal can be identified, then return the
        principal id. Otherwise, return None.

        The request object is fairly opaque. We may decide
        that it implements some generic request interface.

        Implementation note

        It is likely that the component will dispatch
        to another component based on the actual
        request interface. This will allow different
        kinds of requests to be handled correctly.

        For example, a component that authenticates
        based on user names and passwords might request
        an adapter for the request as in::

          getpw=getAdapter(request,
                       ILoginPassword, place=self)

        The place keyword argument is used to control
        where the ILoginPassword component is
        searched for. This is necessary because
        requests are placeless.
        """

    def unauthenticatedPrincipal():
        """Return the id of the unauthenticated principal, if one is defined.
        
        Return None if no unauthenticated principal is defined.

        The unauthenticated principal must be an IUnauthenticatedPrincipal.
        """
        
    def unauthorized(id, request):
        """
        Signal an authorization failure
        
        This method is called when an auhorization problem
        occurs. It can perform a variety of actions, such
        as issuing an HTTP authentication challenge or
        displaying a login interface.
        
        Note that the authentication service nearest to the
        requested resource is called. It is up to
        authentication service implementations to
        colaborate with services higher in the object
        hierarchy.
        
        If no principal has been identified, id will be
        None.
        """

    def getPrincipal(id):
        """
        Get principal meta-data

        Returns an object of type IPrincipal for the given principal
        id. A NotFoundErrorx is raised if the principal cannot be
        found.

        Note that the authentication service nearest to the requested
        resource is called. It is up to authentication service
        implementations to colaborate with services higher in the
        object hierarchy.
        """

    def getPrincipals(name):
        """
        Get principals with matching names.

        Get a iterable object with the principals with names that are
        similar to (e.g. contain) the given name.
        """

