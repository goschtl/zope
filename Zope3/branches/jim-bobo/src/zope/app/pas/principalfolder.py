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

import persistent

import zope.interface
import zope.schema

import zope.app.container.btree
import zope.app.container.contained
import zope.app.container.constraints
import zope.app.container.interfaces

from zope.app.i18n import ZopeMessageIDFactory as _

from zope.app.pas import interfaces

class IInternalPrincipal(zope.interface.Interface):
    """Principal information"""

    login = zope.schema.TextLine(
        title=_("Login"),
        description=_("The Login/Username of the principal. "
                      "This value can change."),
        required=True)

    password = zope.schema.Password(
        title=_(u"Password"),
        description=_("The password for the principal."),
        required=True)

    title = zope.schema.TextLine(
        title=_("Title"),
        description=_("Provides a title for the principal."),
        required=True)

    description = zope.schema.Text(
        title=_("Description"),
        description=_("Provides a description for the principal."),
        required=False,
        missing_value='',
        default=u'',
        )


class IInternalPrincipalContainer(zope.interface.Interface):
    """A container that contains internal principals."""

    prefix = zope.schema.TextLine(
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

    zope.app.container.constraints.contains(IInternalPrincipal)


class IInternalPrincipalContained(zope.interface.Interface):
    """Principal information"""

    zope.app.container.constraints.containers(IInternalPrincipalContainer)


class ISearchSchema(zope.interface.Interface):
    """Search Interface for this Principal Provider"""

    search = zope.schema.TextLine(
        title=_("Search String"),
        description=_("A Search String"),
        required=False,
        default=u'',
        missing_value=u'',
        )

class PrincipalInformation(
    persistent.Persistent,
    zope.app.container.contained.Contained,
    ):
    """An internal principal for Persistent Principal Folder.
    """
    zope.interface.implements(IInternalPrincipal, IInternalPrincipalContained)

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

class PrincipalFolder(zope.app.container.btree.BTreeContainer):
    """A Persistent Principal Folder and Authentication plugin
    """
    zope.interface.implements(interfaces.ISearchableAuthenticationPlugin,
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
        """Add principal information
        """
        # A user with the new login already exists
        if principal.login in self.__id_by_login:
            raise ValueError, 'Principal Login already taken!'

        super(PrincipalFolder, self).__setitem__(id, principal)
        self.__id_by_login[principal.login] = id

    def __delitem__(self, id):
        """Remove principal information
        """
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

        id = self.prefix+id

        return id, {'login': principal.login, 'title': principal.title,
                    'description': principal.description}

    def principalInfo(self, principal_id):
        if principal_id.startswith(self.prefix):
            principal = self.get(principal_id[len(self.prefix):])
            if principal is not None:
                return {
                    'login': principal.login,
                    'title': principal.title,
                    'description': principal.description,
                    }
            

    schema = ISearchSchema

    def search(self, query, start=None, batch_size=None):
        """Search through this principal provider.
        """
        search = query.get('search')
        if search is None:
            return
        i = 0
        n = 1
        for value in self.values():
            if (search in value.title or
                search in value.description or
                search in value.login):
                if not ((start is not None and i < start)
                        or
                        (batch_size is not None and n > batch_size)):
                    n += 1
                    yield self.prefix+value.__name__
                i += 1
