##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Pluggable Authentication service.

$Id$
"""
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.container.interfaces import IContainer, IContained
from zope.app.container.interfaces import IContainerNamesContainer, INameChooser
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.security.interfaces import IAuthenticationService, IPrincipal
from zope.interface import Interface
import zope.schema
from zope.schema import Text, TextLine, Password, Field



class IUserSchemafied(IPrincipal):
    """A User object with schema-defined attributes."""

    login = TextLine(
        title=_("Login"),
        description=_("The Login/Username of the user. "
                      "This value can change."),
        required=True)

    password = Password(
        title=_(u"Password"),
        description=_("The password for the user."),
        required=True)

    def validate(test_password):
        """Confirm whether 'password' is the password of the user."""


class IPluggableAuthentication(Interface):
    """A marker for to mix in a constraints."""


class IPrincipalSource(IContained):
    """A read-only source of IPrincipals where can be added to a auth service.
    """

    __parent__= Field(
        constraint = ContainerTypesConstraint(IPluggableAuthentication))

    def getPrincipal(id):
        """Get principal meta-data.

        Returns an object of type IPrincipal for the given principal
        id. A NotFoundError is raised if the principal cannot be
        found.

        Note that the id has three parts, separated by tabs.  The
        first two part are an authentication service id and a
        principal source id.  The pricipal source will typically need
        to remove the two leading parts from the id when doing it's
        own internal lookup.

        Note that the authentication service nearest to the requested
        resource is called. It is up to authentication service
        implementations to collaborate with services higher in the
        object hierarchy.
        """

    def getPrincipals(name):
        """Get principals with matching names.

        Get a iterable object with the principals with names that are
        similar to (e.g. contain) the given name.
        """


class ILoginPasswordPrincipalSource(IPrincipalSource):
    """ A principal source which can authenticate a user given a
    login and a password """

    def authenticate(login, password):
        """ Return a principal matching the login/password pair.

        If there is no principal in this principal source which
        matches the login/password pair, return None.

        Note: A login is different than an id.  Principals may have
        logins that differ from their id.  For example, a user may
        have a login which is his email address.  He'd like to be able
        to change his login when his email address changes without
        effecting his security profile on the site.
        """


class IPluggableAuthenticationService(IPluggableAuthentication, \
                                      IAuthenticationService, IContainer):
    """An AuthenticationService that can contain multiple pricipal sources.
    
    Inherit from IPluggableAuthentication for to provide a constraints.
    """

    def __setitem__(id, principal_source):
        """Add to object"""
    __setitem__.precondition = ItemTypePrecondition(IPrincipalSource)
  
    def removePrincipalSource(id):
        """Remove a PrincipalSource.

        If id is not present, raise KeyError.
        """


class IContainerPrincipalSource(IPrincipalSource):
    """This is a marker interface for specifying principal sources that are
    also containers. """


class IPrincipalSourceContained(IContained):
    """Make shure we just let object add to IPrincipalSource 
    porvided instances. """

    __parent__ = zope.schema.Field(
        constraint = ContainerTypesConstraint(IPrincipalSource),
        )


class IBTreePrincipalSource(
    ILoginPasswordPrincipalSource,
    IContainerPrincipalSource,
    INameChooser,
    IContainerNamesContainer,
    ):

    def __setitem__(name, principal):
        """Add a principal

        The name must be the same as the principal login
        """

    __setitem__.precondition  = ItemTypePrecondition(IUserSchemafied)


class IBTreePrincipalSourceContained(IPrincipalSourceContained):
    """Set own constarints to the BTreePrincipalSource.
    
    Make shure we just let object add to IBTreePrinicpalSource 
    porvided instances.
    """

    __parent__ = zope.schema.Field(
        constraint = ContainerTypesConstraint(IBTreePrincipalSource),
        )