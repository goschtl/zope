##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Global Authentication Service or Principal Registry

$Id$
"""
from warnings import warn
from zope.interface import implements
from zope.exceptions import NotFoundError
from zope.app import zapi
from zope.app.security.interfaces import ILoginPassword
from zope.app.security.interfaces import IAuthenticationService, IPrincipal
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.site.interfaces import ISimpleService
from zope.app.container.contained import Contained, contained
from warnings import warn

class DuplicateLogin(Exception): pass
class DuplicateId(Exception): pass

class PrincipalRegistry(object):

    implements(IAuthenticationService, ISimpleService)

    # Methods implementing IAuthenticationService

    def authenticate(self, request):
        a = ILoginPassword(request, None)
        if a is not None:
            login = a.getLogin()
            if login is not None:
                p = self.__principalsByLogin.get(login, None)
                if p is not None:
                    password = a.getPassword()
                    if p.validate(password):
                        return p
        return None

    __defaultid = None
    __defaultObject = None

    def defineDefaultPrincipal(self, principal, title, description=''):
        id = principal
        if id in self.__principalsById:
            raise DuplicateId(id)
        self.__defaultid = id
        p = UnauthenticatedPrincipal(principal, title, description)
        self.__defaultObject = contained(p, self, id)
        return p

    def unauthenticatedPrincipal(self):
        return self.__defaultObject

    def unauthorized(self, id, request):
        if id is None or id is self.__defaultid:
            a = ILoginPassword(request)
            a.needLogin(realm="zope")

    def getPrincipal(self, id):
        r = self.__principalsById.get(id)
        if r is None:
            if id == self.__defaultid:
                return self.__defaultObject
            raise NotFoundError(id)
        return r

    def getPrincipalByLogin(self, login):
        r = self.__principalsByLogin.get(login)
        if r is None: raise NotFoundError(login)
        return r

    def getPrincipals(self, name):
        name = name.lower()
        return [p for p in self.__principalsById.itervalues()
                  if p.title.lower().startswith(name) or
                     p.getLogin().lower().startswith(name)]

    # Management methods

    def __init__(self):
        self.__principalsById = {}
        self.__principalsByLogin = {}

    def definePrincipal(self, principal, title, description='',
                        login='', password=''):
        id=principal
        if login in self.__principalsByLogin:
            raise DuplicateLogin(login)

        if id in self.__principalsById or id == self.__defaultid:
            raise DuplicateId(id)

        p = Principal(id, title, description, login, password)
        p = contained(p, self, id)

        self.__principalsByLogin[login] = p
        self.__principalsById[id] = p

        return p

    def _clear(self):
        self.__init__()

principalRegistry = PrincipalRegistry()

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(principalRegistry._clear)
del addCleanUp

class PrincipalBase(Contained):

    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description


class Principal(PrincipalBase):

    implements(IPrincipal)

    def __init__(self, id, title, description, login, pw):
        super(Principal, self).__init__(id, title, description)
        self.__login = login
        self.__pw = pw

    def getLogin(self):
        return self.__login

    def validate(self, pw):
        return pw == self.__pw


class UnauthenticatedPrincipal(PrincipalBase):

    implements(IUnauthenticatedPrincipal)
