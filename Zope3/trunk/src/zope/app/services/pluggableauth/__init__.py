##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Pluggable Authentication service implementation.

$Id: __init__.py,v 1.2 2003/06/23 22:46:17 chrism Exp $
"""

from __future__ import generators
import random
import sys
import datetime
from persistence import Persistent
from zodb.btrees.IOBTree import IOBTree
from zodb.btrees.OIBTree import OIBTree
from zope.interface import implements
from zope.component import getAdapter, queryAdapter
from zope.context.wrapper import Wrapper
from zope.context import getWrapperData
from zope.app.services.servicenames import Authentication
from zope.component.interfaces import IViewFactory
from zope.app.container.btree import BTreeContainer
from zope.app.container.ordered import OrderedContainer
from zope.app.interfaces.container import IContainer
from zope.app.interfaces.container import IContainerNamesContainer
from zope.app.interfaces.container import IOrderedContainer
from zope.app.interfaces.container import IAddNotifiable
from zope.app.interfaces.services.pluggableauth import IUserSchemafied
from zope.app.interfaces.security import ILoginPassword
from zope.app.interfaces.services.pluggableauth \
     import IPluggableAuthenticationService
from zope.app.interfaces.services.pluggableauth import IPrincipalSource
from zope.app.interfaces.services.pluggableauth import IReadPrincipalSource,\
     ILoginPasswordPrincipalSource, IWritePrincipalSource
from zope.app.interfaces.services.service import ISimpleService
from zope.app.component.nextservice import queryNextService
from zope.app.zapi import queryView
from zope.app.traversing import getPath
from zope.context import ContextMethod
from zope.exceptions import NotFoundError
import random

def gen_key():
    """Return a random int (1, MAXINT), suitable for use as a BTree key."""

    return random.randint(0,sys.maxint-1)

class PluggableAuthenticationService(OrderedContainer):

    implements(IPluggableAuthenticationService, ISimpleService,
               IOrderedContainer, IAddNotifiable)

    def __init__(self, earmark=None):
        self.earmark = earmark
        OrderedContainer.__init__(self)

    def afterAddHook(self, object, container):
        """ See IAddNotifiable. """
        if self.earmark is None:
            # XXX need to generate a better earmark that's more likely
            # to be unique and which you can use to actually identify
            # the auth service in error messages
            self.earmark = str(random.randint(0, sys.maxint-1))

    afterAddHook = ContextMethod(afterAddHook)

    def authenticate(self, request):
        """ See IAuthenticationService. """
        for ps_key, ps in self.items():
            loginView = queryView(ps, "login", request)
            if loginView is not None:
                principal = loginView.authenticate()
                if principal is not None:
                    id = '\t'.join((self.earmark, ps_key,
                                    str(principal.getId())))
                    return PrincipalWrapper(principal, self, id=id)

        next = queryNextService(self, Authentication, None)
        if next is not None:
            return next.authenticate(request)

        return None
    authenticate = ContextMethod(authenticate)

    def unauthenticatedPrincipal(self):
        """ See IAuthenticationService. """
        return None # XXX Do we need to implement or use another?

    def unauthorized(self, id, request):
        """ See IAuthenticationService. """

        next = queryNextService(self, Authentication, None)
        if next is not None:
            return next.unauthorized(id, request)

        return None
    unauthorized = ContextMethod(unauthorized)

    def getPrincipal(self, id):
        """ See IAuthenticationService.

        For this implementation, an 'id' is a string which can be
        split into a 3-tuple by splitting on newline characters.  The
        three tuple consists of (auth_service_earmark,
        principal_source_id, principal_id).

        """
        next = None
        
        try:
            auth_svc_earmark, principal_src_id, principal_id = id.split('\t',2)
        except (TypeError, ValueError, AttributeError):
            auth_svc_earmark, principal_src_id, principal_id = None, None, None
            next = queryNextService(self, Authentication, None)

        if auth_svc_earmark != self.earmark:
            next = queryNextService(self, Authentication, None)
        
        if next is not None:
            return next.getPrincipal(id)

        source = self.get(principal_src_id)
        if source is None:
            raise NotFoundError
        p = source.getPrincipal(principal_id)
        return PrincipalWrapper(p, self, id=id)

    getPrincipal = ContextMethod(getPrincipal)

    def getPrincipals(self, name):
        """ See IAuthenticationService. """

        for ps_key, ps in self.items():
            for p in ps.getPrincipals(name):
                id = '\t'.join((self.earmark, ps_key, str(p.getId())))
                yield PrincipalWrapper(p, self, id=id)

        next = queryNextService(self, Authentication, None)
        if next is not None:
            for p in next.getPrincipals(name):
                yield p
    getPrincipals = ContextMethod(getPrincipals)

    def addPrincipalSource(self, id, principal_source):
        """ See IPluggableAuthenticationService.

        >>> pas = PluggableAuthenticationService()
        >>> sps = BTreePrincipalSource()
        >>> pas.addPrincipalSource('simple', sps)
        >>> sps2 = BTreePrincipalSource()
        >>> pas.addPrincipalSource('not_quite_so_simple', sps2)
        >>> pas.keys()
        ['simple', 'not_quite_so_simple']
        """

        if not IReadPrincipalSource.isImplementedBy(principal_source):
            raise TypeError("Source must implement IReadPrincipalSource")
        self.setObject(id, principal_source)
        
    def removePrincipalSource(self, id):
        """ See IPluggableAuthenticationService.

        >>> pas = PluggableAuthenticationService()
        >>> sps = BTreePrincipalSource()
        >>> pas.addPrincipalSource('simple', sps)
        >>> sps2 = BTreePrincipalSource()
        >>> pas.addPrincipalSource('not_quite_so_simple', sps2)
        >>> sps3 = BTreePrincipalSource()
        >>> pas.addPrincipalSource('simpler', sps3)
        >>> pas.keys()
        ['simple', 'not_quite_so_simple', 'simpler']
        >>> pas.removePrincipalSource('not_quite_so_simple')
        >>> pas.keys()
        ['simple', 'simpler']
        """
            
        del self[id]

class BTreePrincipalSource(Persistent):
    """An efficient, scalable provider of Authentication Principals."""

    implements(ILoginPasswordPrincipalSource, IPrincipalSource,
               IContainerNamesContainer)

    def __init__(self):

        self._principals_by_number = IOBTree()
        self._numbers_by_login = OIBTree()

    # IContainer-related methods

    def __delitem__(self, key):
        """ See IContainer.

        >>> sps = BTreePrincipalSource()
        >>> prin = SimplePrincipal('fred', 'fred', '123')
        >>> sps.setObject('fred', prin)
        'fred'
        >>> int(sps.get('fred') == prin)
        1
        >>> del sps['fred']
        >>> int(sps.get('fred') == prin)
        0
        
        """
        number = self._numbers_by_login[key]

        del self._principals_by_number[number]
        del self._numbers_by_login[key]

    def setObject(self, id, object):
        """ See IContainerNamesContainer

        >>> sps = BTreePrincipalSource()
        >>> prin = SimplePrincipal('gandalf', 'shadowfax')
        >>> dummy = sps.setObject('doesntmatter', prin)
        >>> sps.get('doesntmatter')
        """

        store = self._principals_by_number

        key = gen_key()
        while not store.insert(key, object):
            key = gen_key()

        object.id = key
        self._numbers_by_login[object.login] = key

        return object.login

    def keys(self):
        """ See IContainer.

        >>> sps = BTreePrincipalSource()
        >>> sps.keys()
        []
        >>> prin = SimplePrincipal('arthur', 'tea')
        >>> key = sps.setObject('doesntmatter', prin)
        >>> sps.keys()
        ['arthur']
        >>> prin = SimplePrincipal('ford', 'towel')
        >>> key = sps.setObject('doesntmatter', prin)
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
        >>> key = sps.setObject('doesntmatter', prin)
        >>> prin = SimplePrincipal('zaphod', 'gargleblaster')
        >>> key = sps.setObject('doesntmatter', prin)
        >>> [i for i in sps]
        ['trillian', 'zaphod']
        """

        return iter(self.keys())

    def __getitem__(self, key):
        """ See IContainer

        >>> sps = BTreePrincipalSource()
        >>> prin = SimplePrincipal('gag', 'justzisguy')
        >>> key = sps.setObject('doesntmatter', prin)
        >>> sps['gag'].login
        'gag'
        """

        number = self._numbers_by_login[key]
        return self._principals_by_number[number]

    def get(self, key, default=None):
        """ See IContainer

        >>> sps = BTreePrincipalSource()
        >>> prin = SimplePrincipal(1, 'slartibartfast', 'fjord')
        >>> key = sps.setObject('slartibartfast', prin)
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
        >>> key = sps.setObject('doesntmatter', prin)
        >>> [user.login for user in sps.values()]
        ['arthur']
        >>> prin = SimplePrincipal('ford', 'towel')
        >>> key = sps.setObject('doesntmatter', prin)
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
        >>> key = sps.setObject('trillian', prin)
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
        >>> key = sps.setObject('doesntmatter', prin)
        >>> [(k, v.login) for k, v in sps.items()]
        [('zaphod', 'zaphod')]
        >>> prin = SimplePrincipal('marvin', 'paranoid')
        >>> key = sps.setObject('doesntmatter', prin)
        >>> [(k, v.login) for k, v in sps.items()]
        [('marvin', 'marvin'), ('zaphod', 'zaphod')]
        """

        # We're being expensive here (see values() above) for convenience
        return [(p.login, p) for p in self.values()]

    def __contains__(self, key):
        """ See IContainer.

        >>> sps = BTreePrincipalSource()
        >>> prin = SimplePrincipal('slinkp', 'password')
        >>> key = sps.setObject('doesntmatter', prin)
        >>> int('slinkp' in sps)
        1
        >>> int('desiato' in sps)
        0
        """
        return self._numbers_by_login.has_key(key)

    has_key = __contains__

    # PrincipalSource-related methods

    def getPrincipal(self, id):
        """ See IReadPrincipalSource.

        'id' is the id as returned by principal.getId(),
        not a login.

        """
        try:
            id = int(id)
        except TypeError:
            raise NotFoundError
        try:
            return self._principals_by_number[id]
        except KeyError:
            raise NotFoundError

    def getPrincipals(self, name):
        """ See IReadPrincipalSource.

        >>> sps = BTreePrincipalSource()
        >>> prin1 = SimplePrincipal('gandalf', 'shadowfax')
        >>> dummy = sps.setObject('doesntmatter', prin1)
        >>> prin1 = SimplePrincipal('frodo', 'ring')
        >>> dummy = sps.setObject('doesntmatter', prin1)
        >>> prin1 = SimplePrincipal('pippin', 'pipe')
        >>> dummy = sps.setObject('doesntmatter', prin1)
        >>> prin1 = SimplePrincipal('sam', 'garden')
        >>> dummy = sps.setObject('doesntmatter', prin1)
        >>> prin1 = SimplePrincipal('merry', 'food')
        >>> dummy = sps.setObject('doesntmatter', prin1)
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
        if user.validate(password):
            return user

class SimplePrincipal(Persistent):
    """A no-frills IUserSchemafied implementation."""

    implements(IUserSchemafied)

    def __init__(self, login, password, title='', description=''):

        self.id = ''
        self.login = login
        self.password = password
        self.title = title
        self.description = description

    def getId(self):
        """ See IPrincipal. """
        return self.id

    def getTitle(self):
        """ See IPrincipal. """
        return self.title

    def getDescription(self):
        """ See IPrincipal. """
        return self.description

    def getLogin(self):
        """ See IReadUser. """
        return self.login
    
    def validate(self, test_password):
        """ See IReadUser.

        >>> pal = SimplePrincipal('gandalf', 'shadowfax', 'The Grey Wizard',
        ...                       'Cool old man with neato fireworks. '
        ...                       'Has a nice beard.')
        >>> int(pal.validate('shdaowfax'))
        0
        >>> int(pal.validate('shadowfax'))
        1
        """

        return test_password == self.password

class PrincipalAuthenticationView:
    implements(IViewFactory)
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def authenticate(self):
        for interface in (ILoginPassword,):
            a = queryAdapter(self.request, interface, None)
            if a is None:
                return
            login = a.getLogin()
            password = a.getPassword()

            p = self.context.authenticate(login, password)
            return p

    
class PrincipalWrapper(Wrapper):
    """ A wrapper for a principal as returned from the authentication
    service.  The id of the principal as returned by the wrapper is
    a three-tuple instead of the integer id returned by the simple
    principal."""
    def getId(self):
        """ Return the id as passed in to the wrapper """
        return getWrapperData(self)['id']

    
