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
"""ZODB-based Authentication Source

$Id$
"""
__docformat__ = "reStructuredText"

from persistent import Persistent
from zope import interface
from zope import component
from zope.event import notify
from zope.schema import Text, TextLine, Password
from zope.publisher.interfaces import IRequest
from zope.security.interfaces import IGroupAwarePrincipal

from zope.app.container.contained import Contained
from zope.app.container.constraints import contains, containers
from zope.app.container.btree import BTreeContainer
from zope.app.i18n import ZopeMessageIDFactory as _

from zope.app.authentication import interfaces


class IInternalPrincipal(interface.Interface):
    """Principal information"""

    login = TextLine(
        title=_("Login"),
        description=_("The Login/Username of the principal. "
                      "This value can change."))

    password = Password(
        title=_(u"Password"),
        description=_("The password for the principal."))

    title = TextLine(
        title=_("Title"),
        description=_("Provides a title for the principal."))

    description = Text(
        title=_("Description"),
        description=_("Provides a description for the principal."),
        required=False,
        missing_value='',
        default=u'')


class IInternalPrincipalContainer(interface.Interface):
    """A container that contains internal principals."""

    prefix = TextLine(
        title=_("Prefix"),
        description=_(
        "Prefix to be added to all principal ids to assure "
        "that all ids are unique within the authentication service"),
        required=False,
        missing_value=u"",
        default=u'',
        readonly=True)

    contains(IInternalPrincipal)


class IInternalPrincipalContained(interface.Interface):
    """Principal information"""

    containers(IInternalPrincipalContainer)


class ISearchSchema(interface.Interface):
    """Search Interface for this Principal Provider"""

    search = TextLine(
        title=_("Search String"),
        description=_("A Search String"),
        required=False,
        default=u'',
        missing_value=u'')


class InternalPrincipal(Persistent, Contained):
    """An internal principal for Persistent Principal Folder."""

    interface.implements(IInternalPrincipal, IInternalPrincipalContained)

    def __init__(self, login, password, title, description=u''):
        self._login = login
        self.password = password
        self.title = title
        self.description = description

    def getLogin(self):
        return self._login

    def setLogin(self, login):
        oldLogin = self._login
        self._login = login
        if self.__parent__ is not None:
            try:
                self.__parent__.notifyLoginChanged(oldLogin, self)
            except ValueError:
                self._login = oldLogin
                raise

    login = property(getLogin, setLogin)

    def __getitem__(self, attr):
        if attr in ('title', 'description'):
            return getattr(self, attr)


# BBB, alias gone in 3.1
PrincipalInformation = InternalPrincipal


class PrincipalInfo:
    """An implementation of IPrincipalInfo used by the principal folder.

    A principal info is created with id, login, title, and description:

      >>> info = PrincipalInfo('users.foo', 'foo', 'Foo', 'An over-used term.')
      >>> info
      PrincipalInfo('users.foo')
      >>> info.id
      'users.foo'
      >>> info.login
      'foo'
      >>> info.title
      'Foo'
      >>> info.description
      'An over-used term.'

    """
    interface.implements(interfaces.IPrincipalInfo)

    def __init__(self, id, login, title, description):
        self.id = id
        self.login = login
        self.title = title
        self.description = description

    def __repr__(self):
        return 'PrincipalInfo(%r)' % self.id


class PrincipalFolder(BTreeContainer):
    """A Persistent Principal Folder and Authentication plugin.

    See principalfolder.txt for details.
    """

    interface.implements(interfaces.IAuthenticatorPlugin,
                         interfaces.IQueriableAuthenticator,
                         interfaces.IQuerySchemaSearch,
                         IInternalPrincipalContainer)

    schema = ISearchSchema

    def __init__(self, prefix=''):
        self.prefix = unicode(prefix)
        super(PrincipalFolder, self).__init__()
        self.__id_by_login = self._newContainerData()

    def notifyLoginChanged(self, oldLogin, principal):
        """Notify the Container about changed login of a principal.

        We need this, so that our second tree can be kept up-to-date.
        """
        # A user with the new login already exists
        if principal.login in self.__id_by_login:
            raise ValueError, 'Principal Login already taken!'

        del self.__id_by_login[oldLogin]
        self.__id_by_login[principal.login] = principal.__name__

    def __setitem__(self, id, principal):
        """Add principal information."""
        # A user with the new login already exists
        if principal.login in self.__id_by_login:
            raise ValueError, 'Principal Login already taken!'

        super(PrincipalFolder, self).__setitem__(id, principal)
        self.__id_by_login[principal.login] = id

    def __delitem__(self, id):
        """Remove principal information."""
        principal = self[id]
        super(PrincipalFolder, self).__delitem__(id)
        del self.__id_by_login[principal.login]

    def authenticateCredentials(self, credentials):
        """Return principal info if credentials can be authenticated
        """
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None
        id = self.__id_by_login.get(credentials['login'])
        if id is None:
            return None
        internal = self[id]
        if internal.password != credentials['password']:
            return None
        return PrincipalInfo(self.prefix + id, internal.login, internal.title,
                             internal.description)

    def principalInfo(self, id):
        if id.startswith(self.prefix):
            internal = self.get(id[len(self.prefix):])
            if internal is not None:
                return PrincipalInfo(id, internal.login, internal.title,
                                     internal.description)

    def search(self, query, start=None, batch_size=None):
        """Search through this principal provider."""
        search = query.get('search')
        if search is None:
            return
        search = search.lower()
        i = 0
        n = 1
        for value in self.values():
            if (search in value.title.lower() or
                search in value.description.lower() or
                search in value.login.lower()):
                if not ((start is not None and i < start)
                        or (batch_size is not None and n > batch_size)):
                    n += 1
                    yield self.prefix + value.__name__
                i += 1


class Principal:
    """A group-aware implementation of zope.security.interfaces.IPrincipal.

    A principal is created with an ID:

      >>> p = Principal(1)
      >>> p
      Principal(1)
      >>> p.id
      1

    title and description may also be provided:

      >>> p = Principal('george', 'George', 'A site member.')
      >>> p
      Principal('george')
      >>> p.id
      'george'
      >>> p.title
      'George'
      >>> p.description
      'A site member.'

    """
    interface.implements(IGroupAwarePrincipal)

    def __init__(self, id, title=u'', description=u''):
        self.id = id
        self.title = title
        self.description = description
        self.groups = []

    def __repr__(self):
        return 'Principal(%r)' % self.id


class AuthenticatedPrincipalFactory:
    """Creates 'authenticated' principals.

    An authenticated principal is created as a result of an authentication
    operation.

    To use the factory, create it with the info (interfaces.IPrincipalInfo) of
    the principal to create and a request:

      >>> info = PrincipalInfo('users.mary', 'mary', 'Mary', 'The site admin.')
      >>> from zope.publisher.base import TestRequest
      >>> request = TestRequest('/')
      >>> factory = AuthenticatedPrincipalFactory(info, request)
      >>> principal = factory(42)

    The factory uses the info to create a principal with the same ID, title,
    and description:

      >>> principal.id
      'users.mary'
      >>> principal.title
      'Mary'
      >>> principal.description
      'The site admin.'

    It also fires an AuthenticatedPrincipalCreatedEvent:

      >>> from zope.app.event.tests.placelesssetup import getEvents
      >>> [event] = getEvents(interfaces.IAuthenticatedPrincipalCreated)
      >>> event.principal is principal, event.authentication == 42
      (True, True)
      >>> event.info
      PrincipalInfo('users.mary')
      >>> event.request is request
      True

    Listeners can subscribe to this event to perform additional operations
    when the authenticated principal is created.

    For information on how factories are used in the authentication process,
    see README.txt.
    """
    component.adapts(interfaces.IPrincipalInfo, IRequest)

    interface.implements(interfaces.IAuthenticatedPrincipalFactory)

    def __init__(self, info, request):
        self.info = info
        self.request = request

    def __call__(self, authentication):
        principal = Principal(self.info.id, self.info.title,
                              self.info.description)
        notify(interfaces.AuthenticatedPrincipalCreated(
            authentication, principal, self.info, self.request))
        return principal


class FoundPrincipalFactory:
    """Creates 'found' principals.

    A 'found' principal is created as a result of a principal lookup.

    To use the factory, create it with the info (interfaces.IPrincipalInfo) of
    the principal to create:

      >>> info = PrincipalInfo('users.sam', 'sam', 'Sam', 'A site user.')
      >>> factory = FoundPrincipalFactory(info)
      >>> principal = factory(42)

    The factory uses the info to create a principal with the same ID, title,
    and description:

      >>> principal.id
      'users.sam'
      >>> principal.title
      'Sam'
      >>> principal.description
      'A site user.'

    It also fires a FoundPrincipalCreatedEvent:

      >>> from zope.app.event.tests.placelesssetup import getEvents
      >>> [event] = getEvents(interfaces.IFoundPrincipalCreated)
      >>> event.principal is principal, event.authentication == 42
      (True, True)
      >>> event.info
      PrincipalInfo('users.sam')

    Listeners can subscribe to this event to perform additional operations
    when the 'found' principal is created.

    For information on how factories are used in the authentication process,
    see README.txt.
    """
    component.adapts(interfaces.IPrincipalInfo)

    interface.implements(interfaces.IFoundPrincipalFactory)

    def __init__(self, info):
        self.info = info

    def __call__(self, authentication):
        principal = Principal(self.info.id, self.info.title,
                              self.info.description)
        notify(interfaces.FoundPrincipalCreated(authentication,
                                                principal, self.info))
        return principal
