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
"""Authentication service implementation.

$Id: auth.py,v 1.15 2003/05/01 19:35:34 faassen Exp $
"""

from persistence import Persistent
from zodb.btrees.OOBTree import OOBTree

from zope.exceptions import NotFoundError
from zope.component import getAdapter, queryAdapter
from zope.app.services.servicenames import Authentication

from zope.app.interfaces.container import IContainer

from zope.app.interfaces.security import ILoginPassword
from zope.app.interfaces.security import IAuthenticationService

from zope.app.interfaces.services.auth import IAnnotatableUser

from zope.proxy.introspection import removeAllProxies
from zope.app.attributeannotations import AttributeAnnotations
from zope.app.component.nextservice import getNextService
from zope.proxy.context import ContextMethod
from zope.app.interfaces.services.service import ISimpleService


class DuplicateLogin(Exception):
    pass

class DuplicateId(Exception):
    pass


class AuthenticationService(Persistent):

    __implements__ = IAuthenticationService, IContainer, ISimpleService

    def __init__(self):
        self._usersbylogin = OOBTree()
        self._usersbyid = OOBTree()

    def getPrincipalByLogin(self, login):
        try:
            return self._usersbylogin[login]
        except KeyError:
            raise NotFoundError(login)

    def queryPrincipalByLogin(self, login):
        return self._usersbylogin.get(login)

    def authenticate(self, request):
        'See IAuthenticationService'
        a = queryAdapter(request, ILoginPassword, None)
        if a is not None:
            login = a.getLogin()
            if login is not None:
                p = self.queryPrincipalByLogin(login)
                if p is not None:
                    password = a.getPassword()
                    if p.validate(password):
                        return p
                    else:
                        return None
        next = getNextService(self, Authentication)
        return next.authenticate(request)

    authenticate = ContextMethod(authenticate)

    def unauthenticatedPrincipal(self):
        'See IAuthenticationService'
        return None

    def unauthorized(self, id, request):
        'See IAuthenticationService'
        # XXX This is a mess. request has no place here!
        if id is None:
            a = getAdapter(request, ILoginPassword)
            a.needLogin(realm="zope")

    def getPrincipal(self, id):
        'See IAuthenticationService'
        try:
            return self._usersbyid[id]
        except KeyError:
            next = getNextService(self, Authentication)
            return next.getPrincipal(id)

    getPrincipal = ContextMethod(getPrincipal)

    def getPrincipals(self, name):
        'See IAuthenticationService'
        name = name.lower()
        return [p for p in self._usersbylogin.values()
                  if p.getTitle().lower().find(name) >= 0 or
                     p.getLogin().lower().find(name) >= 0 ]

    def __getitem__(self, id):
        'see IItemContainer'
        return self._usersbyid[id]

    def setObject(self, key, object):
        'See IWriteContainer'
        # XXX I think this should generate an id if blank is passed. (RDM)
        if not isinstance(key, (str, unicode)):
            raise TypeError(key)
        try:
            unicode(key)
        except UnicodeError:
            raise TypeError(key)
        if not key:
            raise ValueError(key)
        self._usersbyid[key] = object
        self._usersbylogin[object.getLogin()] = object

    def __delitem__(self, key):
        'See IWriteContainer'
        user = self._usersbyid[key]
        del self._usersbylogin[user.getLogin()]
        del self._usersbyid[key]

    def keys(self):
        'See IEnumerableMapping'
        return self._usersbyid.keys()

    def __iter__(self):
        return iter(self.keys())

    def values(self):
        'See IEnumerableMapping'
        return self._usersbyid.values()

    def items(self):
        'See IEnumerableMapping'
        return self._usersbyid.items()

    def __len__(self):
        'See IEnumerableMapping'
        return len(self._usersbyid)

    def get(self, key, default=None):
        'See IReadMapping'
        return self._usersbyid.get(key, default)

    def __contains__(self,key):
        'See IReadMapping'
        return key in self._usersbyid



class User(Persistent):
    """A persistent implementation of the IUser interface """

    __implements__ =  IAnnotatableUser

    def __init__(self, id, title, description, login, pw):
        self.__id = id
        self.__title = title
        self.__description = description
        self.__login = login
        self.__pw = pw

    def getLogin(self):
        'See IReadUser'
        return self.__login

    def getRoles(self):
        'See IPrincipal'
        annotations = AttributeAnnotations(self)
        roles = annotations.get('roles', [])
        roles = removeAllProxies(roles)
        return roles

    def validate(self, pw):
        'See IReadUser'
        return pw == self.__pw

    def getId(self):
        'See IPrincipal'
        return self.__id

    def getTitle(self):
        'See IPrincipal'
        return self.__title

    def getDescription(self):
        'See IPrincipal'
        return self.__description

    def setTitle(self, title):
        'See IWriteUser'
        self.__title = title

    def setDescription(self, description):
        'See IWriteUser'
        self.__description = description

    def setLogin(self, login):
        'See IWriteUser'

    def setPassword(self, password):
        'See IWriteUser'
        self.__pw = password

    def setRoles(self, roles):
        'See IReadUser'
        annotations = AttributeAnnotations(self)
        annotations['roles'] = roles
