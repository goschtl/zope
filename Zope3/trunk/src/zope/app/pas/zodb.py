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
from BTrees.OOBTree import OOBTree
from UserDict import DictMixin

from zope.interface import implements, Interface
from zope.schema import Text, TextLine, Password, Field

from zope.app.container.btree import BTreeContainer
from zope.app.container.contained import Contained
from zope.app.container.constraints import ItemTypePrecondition
from zope.app.container.constraints import ContainerTypesConstraint
from zope.app.container.interfaces import IContainer
from zope.app.container.interfaces import INameChooser
from zope.app.exception.interfaces import UserError
from zope.app.i18n import ZopeMessageIDFactory as _

import interfaces

class IInternalPrincipal(Interface):
    """Principal information"""

    id = TextLine(
        title=_("Id"),
        description=_("Id as which this principal will be known and used."),
        readonly=True,
        required=True)

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
        required=False)


class IInternalPrincipalContainer(Interface):
    """A container that contains internal principals."""
    
    def __setitem__(id, principal_source):
        """Add to object"""

    __setitem__.precondition = ItemTypePrecondition(IInternalPrincipal)


class IInternalPrincipalContained(Interface):
    """Principal information"""

    __parent__= Field(
        constraint = ContainerTypesConstraint(IInternalPrincipalContainer))


class ISearchSchema(Interface):
    """Search Interface for this Principal Provider"""

    search = TextLine(
        title=_("Search String"),
        description=_("A Search String"),
        required=False,
        default=u'')

class InternalPrincipal(Persistent, Contained, DictMixin):
    """An internal principal for Persistent Principal Folder.

    Make sure the folder gets notified for login changes.

    >>> class Folder:
    ...     def notifyLoginChanged(self, old, principal):
    ...         self.old = old
    ...         self.principal = principal

    >>> folder = Folder()
    >>> principal = InternalPrincipal('1', 'foo', 'bar', 'Foo Bar')
    >>> principal.__parent__ = folder

    >>> principal.login = 'blah'

    >>> folder.old
    'foo'
    >>> folder.principal is principal
    True
    """
    implements(IInternalPrincipal, IInternalPrincipalContained)

    def __init__(self, id, login, password, title, description=u''):
        self.id = id
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
            self.__parent__.notifyLoginChanged(oldLogin, self)

    login = property(getLogin, setLogin)

    def __getitem__(self, attr):
        if attr in ('title', 'description'):
            return getattr(self, attr)

    
        


class PersistentPrincipalFolder(BTreeContainer):
    """A Persistent Principal Folder and Authentication plugin

    Whenever the following code refers to `principal`, we mean a tuple of the
    form (login, password). Since we try not to expose the password, password
    is always `None` in any output.
    """
    implements(interfaces.IAuthenticationPlugin,
               interfaces.IQuerySchemaSearch,
               IInternalPrincipalContainer)

    def __init__(self):
        super(PersistentPrincipalFolder, self).__init__()
        self.__id_by_login = self._newContainerData()

    def notifyLoginChanged(self, oldLogin, principal):
        """Notify the Container about changed login of a principal.

        We need this, so that our second tree can be kept up-to-date.
        """
        # A user with the new login already exists
        if principal.login in self.__id_by_login:
            raise ValueError, 'Principal Login already taken!'

        del self.__id_by_login[oldLogin]
        self.__id_by_login[principal.login] = principal.id
        
    def __setitem__(self, id, principal):
        """ See `IContainerNamesContainer`

        >>> pps = PersistentPrincipalFolder()
        >>> principal = InternalPrincipal('1', 'foo', 'bar', u'Foo Bar')
        >>> pps['1'] = principal
        >>> pps['1'] is principal
        True
        >>> pps._PersistentPrincipalFolder__id_by_login['foo']
        '1'
        """
        principal.id = id
        # A user with the new login already exists
        if principal.login in self.__id_by_login:
            raise ValueError, 'Principal Login already taken!'

        super(PersistentPrincipalFolder, self).__setitem__(id, principal)
        self.__id_by_login[principal.login] = id

    def __delitem__(self, id):
        """ See `IContainer`.

        >>> pps = PersistentPrincipalFolder()
        >>> pps['1'] = InternalPrincipal('1', 'foo', 'bar', u'Foo Bar')
        >>> del pps['1']
        >>> pps['1']
        Traceback (most recent call last):
        ...
        KeyError: '1'
        """
        principal = self[id]
        super(PersistentPrincipalFolder, self).__delitem__(id)
        del self.__id_by_login[principal.login]


    def authenticateCredentials(self, credentials):
        """See zope.app.pas.interfaces.IAuthenticationPlugin

        Create an authentication plugin and add a principal to it.

        >>> pps = PersistentPrincipalFolder()
        >>> pps['1'] = InternalPrincipal('1', 'foo', 'bar', u'Foo Bar')

        >>> pps.authenticateCredentials(1) is None
        True
        >>> pps.authenticateCredentials({'blah': 2}) is None
        True
        >>> pps.authenticateCredentials({'login': 'foo'}) is None
        True
        >>> pps.authenticateCredentials({'password': 'bar'}) is None
        True
        >>> pps.authenticateCredentials({'login': 'foo1',
        ...                              'password': 'bar'}) is None
        True
        >>> pps.authenticateCredentials({'login': 'foo',
        ...                              'password': 'bar1'}) is None
        True
        >>> res=pps.authenticateCredentials({'login': 'foo', 'password': 'bar'})

        >>> import pprint
        >>> pp = pprint.PrettyPrinter(width=65)
        >>> pp.pprint(res)
        ('1', {'login': 'foo', 'description': u'', 'title': u'Foo Bar'})
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

        return id, {'login': principal.login, 'title': principal.title,
                    'description': principal.description}

    def principalInfo(self, principal_id):
        return self.get(principal_id)

    schema = ISearchSchema

    def search(self, query, start=None, batch_size=None):
        """Search through this principal provider.

        >>> pps = PersistentPrincipalFolder()
        >>> pps['1'] = InternalPrincipal('1', 'foo1', 'bar', u'Foo Bar 1')
        >>> pps['2'] = InternalPrincipal('2', 'foo2', 'bar', u'Foo Bar 2')
        >>> pps['3'] = InternalPrincipal('3', 'foo3', 'bar', u'Foo Bar 3')

        >>> list(pps.search({'search': 'foo'}))
        ['1', '2', '3']
        >>> list(pps.search({'search': '1'}))
        ['1']

        >>> list(pps.search({'search': 'foo'}, 1))
        ['2', '3']
        >>> list(pps.search({'search': 'foo'}, 1, 1))
        ['2']
        """
        search = query.get('search', u'') or u''
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
                    yield value.id
                i += 1
        

class NameChooser(object):
    """A name chosser for the principal provider.

    >>> folder = PersistentPrincipalFolder()
    >>> chooser = NameChooser(folder)

    >>> folder['test'] = InternalPrincipal('test', 'foo', 'bar', 'Foo Bar')

    >>> chooser.checkName('test1', None)
    'test1'
    >>> chooser.checkName('test', None)
    Traceback (most recent call last):
    ...
    UserError: Name already taken.

    >>> chooser.chooseName('', InternalPrincipal('foo', 'foo', 'bar', ''))
    'foo'
    """
    implements(INameChooser)

    def __init__(self, container):
        self.container = container

    def checkName(self, name, object):
        if name in self.container:
            raise UserError, 'Name already taken.'
        return name

    def chooseName(self, name, object):
        return object.id
