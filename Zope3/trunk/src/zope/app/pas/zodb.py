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
from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree

from zope.interface import implements

from zope.app.container.interfaces import IContainer
from zope.app.container.contained import Contained

import interfaces


class IPersistentPrincipalStorage(IContainer):
    """Marker Interface"""

class PersistentPrincipalStorage(Persistent, Contained):
    """A Persistent Principal Storage and Authentication plugin

    Whenever the following code refers to `principal`, we mean a tuple of the
    form (login, password). Since we try not to expose the password, password
    is always `None` in any output.
    """
    implements(interfaces.IAuthenticationPlugin, IPersistentPrincipalStorage)

    def __init__(self):
        self._principal_by_id = IOBTree()
        self._id_by_login = OIBTree()

    def __setitem__(self, id, principal):
        """ See `IContainerNamesContainer`

        >>> pps = PersistentPrincipalStorage()
        >>> pps[1] = ('foo', 'bar')
        >>> pps._principal_by_id[1]
        ('foo', 'bar')
        >>> pps._id_by_login['foo']
        1
        """
        self._principal_by_id[id] = principal
        self._id_by_login[principal[0]] = id

    def __delitem__(self, id):
        """ See `IContainer`.

        >>> pps = PersistentPrincipalStorage()
        >>> pps[1] = ('foo', 'bar')
        >>> del pps[1]
        >>> pps[1]
        Traceback (most recent call last):
        ...
        KeyError: 1
        """
        login = self._principal_by_id[id][0]
        del self._principal_by_id[id]
        del self._id_by_login[login]

    def keys(self):
        """ See `IContainer`.

        >>> pps = PersistentPrincipalStorage()
        >>> list(pps.keys())
        []
        >>> pps[1] = ('foo', 'bar')
        >>> list(pps.keys())
        [1]
        >>> del pps[1]
        >>> list(pps.keys())
        []
        """
        return self._principal_by_id.keys()

    def __iter__(self):
        """ See `IContainer`.

        >>> pps = PersistentPrincipalStorage()
        >>> list(pps.keys())
        []
        >>> pps[1] = ('foo', 'bar')
        >>> pps[2] = ('blah', 'baz')
        >>> ids = [i for i in pps]
        >>> ids.sort()
        >>> ids
        [1, 2]
        """
        return iter(self.keys())

    def __getitem__(self, id):
        """ See `IContainer`

        >>> pps = PersistentPrincipalStorage()
        >>> pps[1] = ('foo', 'bar')

        Never expose the password!

        >>> pps[1]
        ('foo', None)
        """
        try:
            return self._principal_by_id[id][0], None
        except TypeError:
            # We were not passed an integer id, for instance
            # because traversal to a view was attempted.
            raise KeyError, id

    def get(self, id, default=None):
        """ See `IContainer`

        >>> pps = PersistentPrincipalStorage()
        >>> marker = object()
        >>> pps.get(1, default=marker) is marker
        True
        >>> pps[1] = ('foo', 'bar')

        Never expose the password!

        >>> pps.get(1)
        ('foo', None)
        """
        try:
            return self[id]
        except KeyError:
            return default

    def values(self):
        """ See `IContainer`.

        >>> pps = PersistentPrincipalStorage()
        >>> pps.values()
        []
        >>> pps[1] = ('foo', 'bar')
        >>> pps.values()
        [('foo', None)]
        """
        return [self[id] for id in self]

    def __len__(self):
        """ See `IContainer`

        >>> pps = PersistentPrincipalStorage()
        >>> len(pps)
        0
        >>> pps[1] = ('foo', 'bar')
        >>> len(pps)
        1
        """
        return len(self._id_by_login)

    def items(self):
        """ See `IContainer`.

        >>> pps = PersistentPrincipalStorage()
        >>> pps.items()
        []
        >>> pps[1] = ('foo', 'bar')
        >>> pps.items()
        [(1, ('foo', None))]
        """
        return [(id, self[id]) for id in self]

    def __contains__(self, id):
        """ See `IContainer`.

        >>> pps = PersistentPrincipalStorage()
        >>> 1 in pps
        False
        >>> pps[1] = ('foo', 'bar')
        >>> 1 in pps
        True
        """
        return id in self.keys()

    has_key = __contains__


    def authenticateCredentials(self, credentials):
        """See zope.app.pas.interfaces.IAuthenticationPlugin

        Create an authentication plugin and add a principal to it.

        >>> pps = PersistentPrincipalStorage()
        >>> pps[1] = ('foo', 'bar')

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
        >>> pps.authenticateCredentials({'login': 'foo', 'password': 'bar'})
        ('1', {'login': 'foo'})
        """
        if not isinstance(credentials, dict):
            return None

        if not ('login' in credentials and 'password' in credentials):
            return None

        id = self._id_by_login.get(credentials['login'])
        if id is None:
            return None

        if self._principal_by_id[id][1] != credentials['password']:
            return None

        return str(id), {'login': credentials['login']}
