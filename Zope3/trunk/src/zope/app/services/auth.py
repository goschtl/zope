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
"""
$Id: auth.py,v 1.3 2002/12/26 18:57:11 jim Exp $
"""
from types import TupleType
from persistence import Persistent

from zope.exceptions import NotFoundError
from zope.component import getAdapter, queryAdapter

from zope.app.interfaces.container import IContainer
from zope.app.container.btree import BTreeContainer

from zope.app.interfaces.security import ILoginPassword
from zope.app.interfaces.security import IAuthenticationService

from zope.app.interfaces.services.auth import IUser

from zope.proxy.introspection import removeAllProxies
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.attributeannotations import AttributeAnnotations
from zope.app.security.grants.principalrole import principalRoleManager



class DuplicateLogin(Exception): pass
class DuplicateId(Exception): pass

class ILocalAuthenticationService(IAuthenticationService, IContainer):
    """TTW manageable authentication service"""

    def getAllUsers():
        """Get all users of the Service."""


class AuthenticationService(BTreeContainer):

    __implements__ = ILocalAuthenticationService

    def __init__(self):
        super(AuthenticationService, self).__init__()

    def getPrincipalByLogin(self, login):
        for p in self.values():
            if p.getLogin() == login:
                return p
        return None

    def getAllUsers(self):
        return self.values()

    def authenticate(self, request):
        'See IAuthenticationService'
        a = queryAdapter(request, ILoginPassword, None)
        if a is not None:
            login = a.getLogin()
            if login is not None:
                p = self.getPrincipalByLogin(login)
                if p is not None:
                    password = a.getPassword()
                    if p.validate(password):
                        return p
        return None

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
        r = self.get(id)
        return r

    def getPrincipals(self, name):
        'See IAuthenticationService'
        name = name.lower()
        return [p for p in self.values()
                  if p.getTitle().lower().startswith(name) or
                     p.getLogin().lower().startswith(name)]


class User(Persistent):
    """A persistent implementation of the IUser interface """

    __implements__ =  IUser, IAttributeAnnotatable

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
        'See IReadUser'
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

    #
    ############################################################
