##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Zope Application-specific Security Interfaces

$Id$
"""
from zope.interface import Interface
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.schema import Text, TextLine
from zope.security.interfaces import IPrincipal, IPermission
from zope.schema.interfaces import ISource

from zope.exceptions import NotFoundError

class PrincipalLookupError(NotFoundError):
    """A prncipal could not be found for a principal id
    """

class IUnauthenticatedPrincipal(IPrincipal):
    """A principal that hasn't been authenticated.

    Authenticated principals are preferable to UnauthenticatedPrincipals.
    """

class IAuthentication(Interface):
    """Provide support for establishing principals for requests.

    This is implemented by performing protocol-specific actions, such as
    issuing challenges or providing login interfaces.

    `IAuthentication` objects are used to implement authentication
    utilities. Because they implement services, they are expected to
    collaborate with services in other contexts. Client code doesn't search a
    context and call multiple services. Instead, client code will call the
    most specific service in a place and rely on the service to delegate to
    other services as necessary.

    The interface doesn't include methods for data management. Services may
    use external data and not allow management in Zope. Simularly, the data to
    be managed may vary with different implementations of a service.
    """

    def authenticate(request):
        """Identify a principal for a request.

        If a principal can be identified, then return the
        principal. Otherwise, return None.

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
        """Return the unauthenticated principal, if one is defined.

        Return None if no unauthenticated principal is defined.

        The unauthenticated principal must be an IUnauthenticatedPrincipal.
        """

    def unauthorized(id, request):
        """Signal an authorization failure.

        This method is called when an auhorization problem
        occurs. It can perform a variety of actions, such
        as issuing an HTTP authentication challenge or
        displaying a login interface.

        Note that the authentication service nearest to the
        requested resource is called. It is up to
        authentication service implementations to
        collaborate with services higher in the object
        hierarchy.

        If no principal has been identified, id will be
        None.
        """

    def getPrincipal(id):
        """Get principal meta-data.

        Returns an object of type IPrincipal for the given principal
        id. A PrincipalLookupError is raised if the principal cannot be
        found.

        Note that the authentication service nearest to the requested
        resource is called. It is up to authentication service
        implementations to collaborate with services higher in the
        object hierarchy.
        """

class IAuthenticationUtility(IAuthentication):
    """This interface is deprecated
    """
    
    def getPrincipals(name):
        """This interface is deprecated
        """

############################################################################
# BBB: 12/15/2004
IAuthenticationService = IAuthenticationUtility
############################################################################

class ILoginPassword(Interface):
    """A password based login.

    An `IAuthentication` would use this (adapting a request),
    to discover the login/password passed from the user, or to
    indicate that a login is required.
    """

    def getLogin():
        """Return login name, or None if no login name found."""

    def getPassword():
        """Return password, or None if no login name found.

        If there's a login but no password, return empty string.
        """

    def needLogin(realm):
        """Indicate that a login is needed.

        The realm argument is the name of the principal registry.
        """

class IPrincipalSource(ISource):
    """A Source of Principal Ids"""

