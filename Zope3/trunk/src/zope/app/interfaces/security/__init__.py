#
# This file is necessary to make this directory a package.

from zope.interface import Interface
from zope.schema.interfaces import IValueSet

class IPrincipal(Interface):
    """Provide information about principals.

    It is likely that IPrincipal objects will have associated views
    used to list principals in management interfaces. For example, a
    system in which other meta-data are provided for principals might
    extend IPrincipal and register a view for the extended interface
    that displays the extended winformation. We'll probably want to
    define a standard view name (e.g.  'inline_summary') for this
    purpose.
    """

    def getId():
        """Return a unique id string for the principal."""

    def getTitle():
        """Return a label for the principal

        The label will be used in interfaces to allow users to make
        security assertions (e.g. role or permission
        assignments) about principals.
        """

    def getDescription():
        """Return a description of the principal."""

    def getRoles():
        """Return a possibly empty list of ids of roles held by this principal.
        """


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
        colaborate with services higher in the object
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
        implementations to colaborate with services higher in the
        object hierarchy.
        """

    def getPrincipals(name):
        """Get principals with matching names.

        Get a iterable object with the principals with names that are
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


class IRole(IRegisteredObject):
    """A role object."""

class IRoleService(Interface):
    """Define roles

     'IRoleService' objects are used to implement role-definition
     services. Because they implement services, they are expected to
     collaborate with services in other contexts. Client code doesn't
     sarch a context and call multiple services. Instead, client code
     will call the most specific service in a place and rely on the
     service to delegate to other services as necessary.

     The interface doesn't include methods for data
     management. Services may use external data and not allow
     management in Zope. Simularly, the data to be managed may vary
     with different implementations of a service.
     """

    def getRole(rid):
        """Return an 'IRole' object for the given role id."""


    def getRoles():
        """Return a sequence of the roles (IRole objects)
        defined in the place containing the service."""




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

class IPermissionField(IValueSet):
    u"""Fields with Permissions as values
    """

class IPrincipalRoleMap(Interface):
    """Mappings between principals and roles."""

    def getPrincipalsForRole(role_id):
        """Get the principals that have been granted a role.

        Return the list of (principal id, setting) who have been assigned or
        removed from a role.

        If no principals have been assigned this role,
        then the empty list is returned.
        """

    def getRolesForPrincipal(principal_id):
        """Get the roles granted to a principal.

        Return the list of (role id, setting) assigned or removed from
        this principal.

        If no roles have been assigned to
        this principal, then the empty list is returned.
        """

    def getSetting(role_id, principal_id):
        """Return the setting for this principal, role combination
        """

    def getPrincipalsAndRoles():
        """Get all settings.

        Return all the principal/role combinations along with the
        setting for each combination as a sequence of tuples with the
        role id, principal id, and setting, in that order.
        """


class IPrincipalRoleManager(IPrincipalRoleMap):
    """Management interface for mappings between principals and roles."""

    def assignRoleToPrincipal(role_id, principal_id):
        """Assign the role to the principal."""

    def removeRoleFromPrincipal(role_id, principal_id):
        """Remove a role from the principal."""

    def unsetRoleForPrincipal(role_id, principal_id):
        """Unset the role for the principal."""


class IRolePermissionMap(Interface):
    """Mappings between roles and permissions."""

    def getPermissionsForRole(role_id):
        """Get the premissions granted to a role.

        Return a sequence of (permission id, setting) tuples for the given
        role.

        If no permissions have been granted to this
        role, then the empty list is returned.
        """

    def getRolesForPermission(permission_id):
        """Get the roles that have a permission.

        Return a sequence of (role id, setting) tuples for the given
        permission.

        If no roles have been granted this permission, then the empty list is
        returned.
        """

    def getSetting(permission_id, role_id):
        """Return the setting for the given permission id and role id

        If there is no setting, Unset is returned
        """

    def getRolesAndPermissions():
        """Return a sequence of (permission_id, role_id, setting) here.

        The settings are returned as a sequence of permission, role,
        setting tuples.

        If no principal/role assertions have been made here, then the empty
        list is returned.
        """


class IRolePermissionManager(IRolePermissionMap):
    """Management interface for mappings between roles and permissions."""

    def grantPermissionToRole(permission_id, role_id):
        """Bind the permission to the role.
        """

    def denyPermissionToRole(permission_id, role_id):
        """Deny the permission to the role
        """

    def unsetPermissionFromRole(permission_id, role_id):
        """Clear the setting of the permission to the role.
        """


class IPrincipalPermissionMap(Interface):
    """Mappings between principals and permissions."""

    def getPrincipalsForPermission(permission_id):
        """Get the principas that have a permission.

        Return the list of (principal_id, setting) tuples that describe
        security assertions for this permission.

        If no principals have been set for this permission, then the empty
        list is returned.
        """

    def getPermissionsForPrincipal(principal_id):
        """Get the permissions granted to a principal.

        Return the list of (permission, setting) tuples that describe
        security assertions for this principal.

        If no permissions have been set for this principal, then the empty
        list is returned.
        """

    def getSetting(permission_id, principal_id):
        """Get the setting for a permission and principal.

        Get the setting (Allow/Deny/Unset) for a given permission and
        principal.
        """

    def getPrincipalsAndPermissions():
        """Get all principal permission settings.

        Get the principal security assertions here in the form
        of a list of three tuple containing
        (permission id, principal id, setting)
        """


class IPrincipalPermissionManager(IPrincipalPermissionMap):
    """Management interface for mappings between principals and permissions."""

    def grantPermissionToPrincipal(permission_id, principal_id):
        """Assert that the permission is allowed for the principal.
        """

    def denyPermissionToPrincipal(permission_id, principal_id):
        """Assert that the permission is denied to the principal.
        """

    def unsetPermissionForPrincipal(permission_id, principal_id):
        """Remove the permission (either denied or allowed) from the
        principal.
        """
