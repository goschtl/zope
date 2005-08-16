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

import zope.interface
from zope.schema import Text, TextLine, Password

from zope.app.authentication import interfaces

from persistent import Persistent
from zope.interface import Interface, implements
from zope.app.container.contained import Contained
from zope.app.container.constraints import contains, containers
from zope.app.container.btree import BTreeContainer
from zope.app.i18n import ZopeMessageIDFactory as _


class IInternalPrincipal(Interface):
    """Principal information"""

    login = TextLine(
        title=_("Login"),
        description=_("The Login/Username of the principal. "
                      "This value can change."),
        required=True)

    password = Password(
        title=_(u"Password"),
        description=_("The password for the principal."),
        required=True)

    title = TextLine(
        title=_("Title"),
        description=_("Provides a title for the principal."),
        required=True)

    description = Text(
        title=_("Description"),
        description=_("Provides a description for the principal."),
        required=False,
        missing_value='',
        default=u'',
        )


class IInternalPrincipalContainer(Interface):
    """A container that contains internal principals."""

    prefix = TextLine(
        title=_("Prefix"),
        description=_(
        "Prefix to be added to all principal ids to assure "
        "that all ids are unique within the authentication service"
        ),
        required=False,
        missing_value=u"",
        default=u'',
        readonly=True,
        )

    contains(IInternalPrincipal)


class IInternalPrincipalContained(Interface):
    """Principal information"""

    containers(IInternalPrincipalContainer)


class ISearchSchema(Interface):
    """Search Interface for this Principal Provider"""

    search = zope.schema.TextLine(
        title=_("Search String"),
        description=_("A Search String"),
        required=False,
        default=u'',
        missing_value=u'',
        )


class PrincipalInformation(Persistent, Contained):
    """An internal principal for Persistent Principal Folder."""

    implements(IInternalPrincipal, IInternalPrincipalContained)

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


class PrincipalFolder(BTreeContainer):
    """A Persistent Principal Folder and Authentication plugin."""

    implements(interfaces.ISearchableAuthenticationPlugin,
               interfaces.IQuerySchemaSearch,
               IInternalPrincipalContainer)

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

        principal = self[id]
        if principal.password != credentials['password']:
            return None

        id = self.prefix + id

        return id, {'login': principal.login,
                    'title': principal.title,
                    'description': principal.description}

    def principalInfo(self, principal_id):
        if principal_id.startswith(self.prefix):
            principal = self.get(principal_id[len(self.prefix):])
            if principal is not None:
                return {'login': principal.login,
                        'title': principal.title,
                        'description': principal.description}

    schema = ISearchSchema

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
