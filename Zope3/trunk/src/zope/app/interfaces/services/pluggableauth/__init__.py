##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Pluggable Authentication service.

$Id: __init__.py,v 1.8 2003/09/21 17:32:29 jim Exp $
"""
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.container import IContainer 
from zope.app.interfaces.security import IAuthenticationService, IPrincipal
from zope.interface import Interface
from zope.schema import Text, TextLine, Password

class IUserSchemafied(IPrincipal):
    """A User object with schema-defined attributes."""

    id = TextLine(
        title=_("Id"),
        description=_("The unique identification of the user"),
        required=True,
        readonly=True)

    title = TextLine(
        title=_("Title"),
        description=_("The title of the user. "
                      "This is usually used in the UI."),
        required=False)

    description = Text(
        title=_("Description"),
        description=_("A detailed description of the user."),
        required=False)

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

class IPluggableAuthenticationService(IAuthenticationService):
    """An AuthenticationService that can contain multiple pricipal sources.
    """

    def addPrincipalSource(id, principal_source):
        """Add an IReadPrincipalSource to the end of our OrderedContainer.

        If id is already present or invalid (according to site
        policy), raise KeyError.

        If principal_source does not implement IReadPrincipalSource,
        raise TypeError
        """

    def removePrincipalSource(id):
        """Remove a PrincipalSource.

        If id is not present, raise KeyError.
        """

class IPrincipalSource(Interface):
    """A read-only source of IPrincipals.
    """

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
        effecting his security profile on the site.  """


class IContainerPrincipalSource(IPrincipalSource, IContainer):
    """This is a marker interface for specifying principal sources that are
    also containers. """
