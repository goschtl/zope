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
$Id: AuthenticationService.py,v 1.1 2002/07/13 16:52:57 srichter Exp $
"""
from types import TupleType

from Persistence import PersistentMapping
from Zope.Exceptions import NotFoundError
from Zope.ComponentArchitecture import getAdapter, queryAdapter

from Zope.App.OFS.Container.IContainer import IHomogenousContainer, IContainer
from Zope.App.OFS.Container.BTreeContainer import BTreeContainer

from Zope.App.Security.ILoginPassword import ILoginPassword
from Zope.App.Security.IAuthenticationService import IAuthenticationService

from Zope.App.OFS.Services.AuthenticationService.IUser import IUser

class DuplicateLogin(Exception): pass
class DuplicateId(Exception): pass

class ILocalAuthenticationService(IAuthenticationService, IContainer,
                                  IHomogenousContainer):
    """TTW manageable authentication service"""


class AuthenticationService(BTreeContainer):

    __implements__ = ILocalAuthenticationService

    def __init__(self):
        super(AuthenticationService, self).__init__()

    def getPrincipalByLogin(self, login):
        for p in self.values():
            if p.getLogin() == login:
                return p
        return None

    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.Services.AuthenticationService.AuthenticationService.

    ######################################
    # from: Zope.App.Security.IAuthenticationService.IAuthenticationService

    def authenticate(self, request):
        'See Zope.App.Security.IAuthenticationService.IAuthenticationService'
        a = queryAdapter(request, ILoginPassword, None)
        if a is not None:
            login = a.getLogin()
            if login is not None:
                p = self.getPrincipalByLogin(login)
                if p is not None:
                    password = a.getPassword()
                    if p.validate(password):
                        return p.getId()
        return None

    def unauthenticatedPrincipal(self):
        'See Zope.App.Security.IAuthenticationService.IAuthenticationService'
        return None

    def unauthorized(self, id, request):
        'See Zope.App.Security.IAuthenticationService.IAuthenticationService'
        # XXX This is a mess. request has no place here!
        if id is None:
            a = getAdapter(request, ILoginPassword)
            a.needLogin(realm="zope")

    def getPrincipal(self, id):
        'See Zope.App.Security.IAuthenticationService.IAuthenticationService'
        r = self.get(id)
        return r

    def getPrincipals(self, name):
        'See Zope.App.Security.IAuthenticationService.IAuthenticationService'
        name = name.lower()
        return [p for p in self.values()
                  if p.getTitle().lower().startswith(name) or
                     p.getLogin().lower().startswith(name)]

    ######################################
    # from: Zope.App.OFS.Container.IContainer.IHomogenousContainer

    def isAddable(self, interfaces):
        'See Zope.App.OFS.Container.IContainer.IHomogenousContainer'
        if type(interfaces) != TupleType:
            interfaces = (interfaces,)
        if IUser in interfaces:
            return 1
        return 0

    #
    ############################################################
