##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Pluggable Authentication service implementation.

$Id: __init__.py 26176 2004-07-07 18:34:31Z jim $
"""
import sys
import random

from persistent import Persistent
from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree

from zope.interface import implements
from zope.exceptions import NotFoundError

from zope.app.container.contained import Contained, setitem, uncontained

from interfaces import IContainerPrincipalSource
from interfaces import IBTreePrincipalSource

from exception import LoginNameTaken
from principal import SimplePrincipal



def gen_key():
    """Return a random int (1, MAXINT), suitable for use as a BTree key."""

    return random.randint(0, sys.maxint-1)


class BTreePrincipalSource(Persistent, Contained):
    """An efficient, scalable provider of Authentication Principals."""

    implements(IBTreePrincipalSource)

    def __init__(self):

        self._principals_by_number = IOBTree()
        self._numbers_by_login = OIBTree()

    # IContainer-related methods

    def __delitem__(self, login):
        """ See IContainer.

        >>> sps = BTreePrincipalSource()
        >>> prin = SimplePrincipal('fred', 'fred', '123')
        >>> sps['fred'] = prin
        >>> int(sps.get('fred') == prin)
        1
        >>> del sps['fred']
        >>> int(sps.get('fred') == prin)
        0

        """
        number = self._numbers_by_login[login]

        uncontained(self._principals_by_number[number], self, login)
        del self._principals_by_number[number]
        del self._numbers_by_login[login]

    def __setitem__(self, login, ob):
        """ See IContainerNamesContainer

        >>> sps = BTreePrincipalSource()
        >>> prin = SimplePrincipal('gandalf', 'shadowfax')
        >>> sps['doesntmatter'] = prin
        >>> sps.get('doesntmatter')
        """
        setitem(self, self.__setitem, login, ob)

    def __setitem(self, login, ob):
        store = self._principals_by_number

        key = gen_key()
        while not store.insert(key, ob):
            key = gen_key()

        ob.id = key
        self._numbers_by_login[ob.login] = key

    def keys(self):
        """ See IContainer.

        >>> sps = BTreePrincipalSource()
        >>> sps.keys()
        []
        >>> prin = SimplePrincipal('arthur', 'tea')
        >>> sps['doesntmatter'] = prin
        >>> sps.keys()
        ['arthur']
        >>> prin = SimplePrincipal('ford', 'towel')
        >>> sps['doesntmatter'] = prin
        >>> sps.keys()
        ['arthur', 'ford']
        """

        return list(self._numbers_by_login.keys())

    def __iter__(self):
        """ See IContainer.

        >>> sps = BTreePrincipalSource()
        >>> sps.keys()
        []
        >>> prin = SimplePrincipal('trillian', 'heartOfGold')
        >>> sps['doesntmatter'] = prin
        >>> prin = SimplePrincipal('zaphod', 'gargleblaster')
        >>> sps['doesntmatter'] = prin
        >>> [i for i in sps]
        ['trillian', 'zaphod']
        """

        return iter(self.keys())

    def __getitem__(self, key):
        """ See IContainer

        >>> sps = BTreePrincipalSource()
        >>> prin = SimplePrincipal('gag', 'justzisguy')
        >>> sps['doesntmatter'] = prin
        >>> sps['gag'].login
        'gag'
        """

        number = self._numbers_by_login[key]
        return self._principals_by_number[number]

    def get(self, key, default=None):
        """ See IContainer

        >>> sps = BTreePrincipalSource()
        >>> prin = SimplePrincipal(1, 'slartibartfast', 'fjord')
        >>> sps['slartibartfast'] = prin
        >>> principal = sps.get('slartibartfast')
        >>> sps.get('marvin', 'No chance, dude.')
        'No chance, dude.'
        """

        try:
            number = self._numbers_by_login[key]
        except KeyError:
            return default

        return self._principals_by_number[number]

    def values(self):
        """ See IContainer.

        >>> sps = BTreePrincipalSource()
        >>> sps.keys()
        []
        >>> prin = SimplePrincipal('arthur', 'tea')
        >>> sps['doesntmatter'] = prin
        >>> [user.login for user in sps.values()]
        ['arthur']
        >>> prin = SimplePrincipal('ford', 'towel')
        >>> sps['doesntmatter'] = prin
        >>> [user.login for user in sps.values()]
        ['arthur', 'ford']
        """

        return [self._principals_by_number[n]
                for n in self._numbers_by_login.values()]

    def __len__(self):
        """ See IContainer

        >>> sps = BTreePrincipalSource()
        >>> int(len(sps) == 0)
        1
        >>> prin = SimplePrincipal(1, 'trillian', 'heartOfGold')
        >>> sps['trillian'] = prin
        >>> int(len(sps) == 1)
        1
        """

        return len(self._principals_by_number)

    def items(self):
        """ See IContainer.

        >>> sps = BTreePrincipalSource()
        >>> sps.keys()
        []
        >>> prin = SimplePrincipal('zaphod', 'gargleblaster')
        >>> sps['doesntmatter'] = prin
        >>> [(k, v.login) for k, v in sps.items()]
        [('zaphod', 'zaphod')]
        >>> prin = SimplePrincipal('marvin', 'paranoid')
        >>> sps['doesntmatter'] = prin
        >>> [(k, v.login) for k, v in sps.items()]
        [('marvin', 'marvin'), ('zaphod', 'zaphod')]
        """

        # We're being expensive here (see values() above) for convenience
        return [(p.login, p) for p in self.values()]

    def __contains__(self, key):
        """ See IContainer.

        >>> sps = BTreePrincipalSource()
        >>> prin = SimplePrincipal('slinkp', 'password')
        >>> sps['doesntmatter'] = prin
        >>> int('slinkp' in sps)
        1
        >>> int('desiato' in sps)
        0
        """
        return self._numbers_by_login.has_key(key)

    has_key = __contains__

    # PrincipalSource-related methods

    def getPrincipal(self, id):
        """ See IPrincipalSource.

        'id' is the id as returned by principal.getId(),
        not a login.

        """

        id = id.split('\t')[2]
        id = int(id)

        try:
            return self._principals_by_number[id]
        except KeyError:
            raise NotFoundError, id

    def getPrincipals(self, name):
        """ See IPrincipalSource.

        >>> sps = BTreePrincipalSource()
        >>> prin1 = SimplePrincipal('gandalf', 'shadowfax')
        >>> sps['doesntmatter'] = prin1
        >>> prin1 = SimplePrincipal('frodo', 'ring')
        >>> sps['doesntmatter'] = prin1
        >>> prin1 = SimplePrincipal('pippin', 'pipe')
        >>> sps['doesntmatter'] = prin1
        >>> prin1 = SimplePrincipal('sam', 'garden')
        >>> sps['doesntmatter'] = prin1
        >>> prin1 = SimplePrincipal('merry', 'food')
        >>> sps['doesntmatter'] = prin1
        >>> [p.login for p in sps.getPrincipals('a')]
        ['gandalf', 'sam']
        >>> [p.login for p in sps.getPrincipals('')]
        ['frodo', 'gandalf', 'merry', 'pippin', 'sam']
        >>> [p.login for p in sps.getPrincipals('sauron')]
        []
        """

        for k in self.keys():
            if k.find(name) != -1:
                yield self[k]

    def authenticate(self, login, password):
        """ See ILoginPasswordPrincipalSource. """
        number = self._numbers_by_login.get(login)
        if number is None:
            return
        user = self._principals_by_number[number]
        if user.password == password:
            return user


    def checkName(self, name, object):
        """Check to make sure the name is valid

        Don't allow suplicate names:

        >>> sps = BTreePrincipalSource()
        >>> prin1 = SimplePrincipal('gandalf', 'shadowfax')
        >>> sps['gandalf'] = prin1
        >>> sps.checkName('gandalf', prin1)
        Traceback (most recent call last):
        ...
        LoginNameTaken: gandalf

        """
        if name in self._numbers_by_login:
            raise LoginNameTaken(name)

    def chooseName(self, name, object):
        """Choose a name for the principal

        Always choose the object's existing name:

        >>> sps = BTreePrincipalSource()
        >>> prin1 = SimplePrincipal('gandalf', 'shadowfax')
        >>> sps.chooseName(None, prin1)
        'gandalf'

        """
        return object.login
