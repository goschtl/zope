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
"""A persistent implementation of thr IPrincipal interface

$Id: User.py,v 1.1 2002/07/13 16:52:57 srichter Exp $
"""
from Persistence import Persistent
from Zope.App.OFS.Annotation.IAnnotatable import IAnnotatable
from Zope.App.OFS.Services.AuthenticationService.IUser import IUser

class User(Persistent):
    """A persistent implementation of the IUser interface """
    
    __implements__ =  IUser, IAnnotatable

    def __init__(self, id, title, description, login, pw):
        self.__id = id
        self.__title = title
        self.__description = description
        self.__login = login
        self.__pw = pw

    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.Services.AuthenticationService.IUser.

    ######################################
    # from: Zope.App.OFS.Services.AuthenticationService.IUser.IReadUser

    def getLogin(self):
        'See Zope.App.OFS.Services.AuthenticationService.IUser.IReadUser'
        return self.__login

    def validate(self, pw):
        'See Zope.App.OFS.Services.AuthenticationService.IUser.IReadUser'
        return pw == self.__pw

    ######################################
    # from: Zope.App.Security.IPrincipal.IPrincipal

    def getId(self):
        'See Zope.App.Security.IPrincipal.IPrincipal'
        return self.__id

    def getTitle(self):
        'See Zope.App.Security.IPrincipal.IPrincipal'
        return self.__title

    def getDescription(self):
        'See Zope.App.Security.IPrincipal.IPrincipal'
        return self.__description

    ######################################
    # from: Zope.App.OFS.Services.AuthenticationService.IUser.IWriteUser

    def setTitle(self, title):
        'See Zope.App.OFS.Services.AuthenticationService.IUser.IWriteUser'
        self.__title = title

    def setDescription(self, description):
        'See Zope.App.OFS.Services.AuthenticationService.IUser.IWriteUser'
        self.__description = description

    def setLogin(self, login):
        'See Zope.App.OFS.Services.AuthenticationService.IUser.IWriteUser'

    def setPassword(self, password):
        'See Zope.App.OFS.Services.AuthenticationService.IUser.IWriteUser'
        self.__pw = password
    #
    ############################################################
