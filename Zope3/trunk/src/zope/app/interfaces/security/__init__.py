#
# This file is necessary to make this directory a package.

from zope.interface import Interface
from zope.schema.interfaces import IEnumerated, IField

class IRegisteredObject(Interface):

    def getId():
        """Get the id of the registered object."""

    def getTitle():
        """Get the human readable title of the registered object.
        Must be a string, but it may be empty.
        """

    def getDescription():
        """Get the human readable description of the registered object.
        Must be a string, but it may be empty.
        """



class IPrincipal(Interface):
    """Provide information about principals.

    It is likely that IPrincipal objects will have associated views
    used to list principals in management interfaces. For example, a
    system in which other meta-data are provided for principals might
    extend IPrincipal and register a view for the extended interface
    that displays the extended information. We'll probably want to
    define a standard view name (e.g.  'inline_summary') for this
    purpose.
    """

    def getId():
        """Return a unique id string for the principal."""

    def getTitle():
        """Return a label for the principal

        The label will be used in interfaces to allow users to make
        security assertions about principals.
        """

    def getDescription():
        """Return a description of the principal."""


class IUnauthenticatedPrincipal(IPrincipal):
    """A principal that hasn't been authenticated.

    Authenticated principals are preferable to UnauthenticatedPrincipals.
    """


class IAuthenticationService(Interface):
    """Provide support for establishing principals for requests.

    This is implemented by performing protocol-specific actions,
    such as issuing challenges or providing login interfaces.

    IAuthenticationService objects are used to implement
    authentication services. Because they implement services, they are
    expected to collaborate with services in other contexts. Client
    code doesn't search a context and call multiple services. Instead,
    client code will call the most specific service in a place and
    rely on the service to delegate to other services as necessary.

    The interface doesn't include methods for data
    management. Services may use external data and not allow
    management in Zope. Simularly, the data to be managed may vary
    with different implementations of a service.
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
        id. A NotFoundError is raised if the principal cannot be
        found.

        Note that the authentication service nearest to the requested
        resource is called. It is up to authentication service
        implementations to collaborate with services higher in the
        object hierarchy.
        """

    def getPrincipals(name):
        """Get principals with matching names.

        Get an iterable object with the principals with names that are
        similar to (e.g. contain) the given name.
        """

class ILoginPassword(Interface):
    """A password based login.

    An IAuthenticationService would use this (adapting a request),
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

class IPermission(IRegisteredObject):
    """A permission object."""

class IPermissionService(Interface):

    """Manage information about permissions

     'IPermissionService' objects are used to implement
     permission-definition services. Because they implement services,
     they are expected to collaborate with services in other
     contexts. Client code doesn't search a context and call multiple
     services. Instead, client code will call the most specific
     service in a place and rely on the service to delegate to other
     services as necessary.

     The interface doesn't include methods for data
     management. Services may use external data and not allow
     management in Zope. Similarly, the data to be managed may vary
     with different implementations of a service.
     """

    def getPermission(permission_id):
        """Get permission information

        Return an 'IPermission' object for the
        given permission id.  Return None if there is no permission defined
        """

    def getPermissions():
        """Get the defined permissions

        Return a sequence of the permissions
        (IPermission objects) defined in the place containing the
        service.
        """

class IPermissionField(IEnumerated, IField):
    u"""Fields with Permissions as values
    """

