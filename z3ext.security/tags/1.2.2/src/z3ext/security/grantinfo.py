##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
""" IExtendedGrantInfo implmentation, extended version of IGrantInfo

$Id$
"""

from zope import interface, component
from zope.component import getAdapters
from zope.security.proxy import removeSecurityProxy

from zope.securitypolicy.interfaces import IPrincipalRoleMap
from zope.securitypolicy.interfaces import IRolePermissionMap

from zope.securitypolicy.principalrole import principalRoleManager
globalPrincipalsForRole = principalRoleManager.getPrincipalsForRole

from interfaces import IExtendedGrantInfo
from securitypolicy import globalRolesForPrincipal, globalRolesForPermission


class ExtendedGrantInfo(object):
    component.adapts(interface.Interface)
    interface.implements(IExtendedGrantInfo)

    def __init__(self, context):
        self.context = context

    def getRolesForPermission(self, permission):
        context = removeSecurityProxy(self.context)

        roles = {}
        for name, roleperm in getAdapters((context,), IRolePermissionMap):
            for role, setting in roleperm.getRolesForPermission(permission):
                if role not in roles:
                    roles[role] = setting

        parent = getattr(context, '__parent__', None)
        if parent is None:
            for name, setting in globalRolesForPermission(permission):
                if name not in roles:
                    roles[name] = setting
        else:
            info = IExtendedGrantInfo(parent)
            for role, setting in info.getRolesForPermission(permission):
                if role not in roles:
                    roles[role] = setting

        return roles.items()

    def getRolesForPrincipal(self, principal):
        context = removeSecurityProxy(self.context)

        roles = {}
        for name, prinrole in getAdapters((context,), IPrincipalRoleMap):
            for role, setting in prinrole.getRolesForPrincipal(principal):
                if role not in roles:
                    roles[role] = setting

        parent = getattr(context, '__parent__', None)
        if parent is None:
            for role, setting in globalRolesForPrincipal(principal):
                if role not in roles:
                    roles[role] = setting
        else:
            info = IExtendedGrantInfo(parent)
            for role, setting in info.getRolesForPrincipal(principal):
                if role not in roles:
                    roles[role] = setting

        return roles.items()

    def getPrincipalsForRole(self, role):
        context = removeSecurityProxy(self.context)

        principals = {}
        for name, prinrole in getAdapters((context,), IPrincipalRoleMap):
            for principal, setting in prinrole.getPrincipalsForRole(role):
                if principal not in principals:
                    principals[principal] = setting

        parent = getattr(context, '__parent__', None)
        if parent is None:
            for principal, setting in globalPrincipalsForRole(role):
                if principal not in principals:
                    principals[principal] = setting
        else:
            info = IExtendedGrantInfo(parent)
            for principal, setting in info.getPrincipalsForRole(role):
                if principal not in principals:
                    principals[principal] = setting

        return principals.items()
