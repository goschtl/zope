##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
""" Define Zope\'s default security policy

$Id: ZopeSecurityPolicy.py,v 1.2 2002/06/10 23:28:16 jim Exp $
"""
__version__='$Revision: 1.2 $'[11:-2]

from Zope.ComponentArchitecture import queryAdapter
from Zope.Proxy.ContextWrapper import ContainmentIterator
from Zope.Exceptions import Unauthorized, Forbidden
from Zope.Security.ISecurityPolicy import ISecurityPolicy
from Zope.App.Security.IRolePermissionManager import IRolePermissionManager
from Zope.App.Security.IPrincipalPermissionManager \
    import IPrincipalPermissionManager
from Zope.App.Security.IPrincipalRoleManager \
    import IPrincipalRoleManager
from Zope.App.Security.IRolePermissionManager import IRolePermissionManager
from Zope.App.Security.PermissionRegistry import permissionRegistry 
from Zope.App.Security.PrincipalRegistry import principalRegistry 
from Zope.App.Security.RoleRegistry import roleRegistry
from Zope.App.Security.PrincipalPermissionManager \
     import principalPermissionManager 
from Zope.App.Security.RolePermissionManager import rolePermissionManager 
from Zope.App.Security.PrincipalRoleManager import principalRoleManager
from Zope.App.Security.Settings import Allow, Deny, Assign, Remove, Unset

from types import StringType, StringTypes, TupleType, ListType, IntType, MethodType, NoneType

getPermissionsForPrincipal = \
                principalPermissionManager.getPermissionsForPrincipal
getPermissionsForRole      = rolePermissionManager.getPermissionsForRole
getRolesForPrincipal       = principalRoleManager.getRolesForPrincipal

globalContext=object()

class ZopeSecurityPolicy:

    __implements__ = ISecurityPolicy

    def __init__(self, ownerous=1, authenticated=1):
        """
            Two optional keyword arguments may be provided:

            ownerous -- Untrusted users can create code
                (e.g. Python scripts or templates),
                so check that code owners can access resources.
                The argument must have a truth value.
                The default is true.

            authenticated -- Allow access to resources based on the
                privaledges of the authenticated user.  
                The argument must have a truth value.
                The default is true.

                This (somewhat experimental) option can be set
                to false on sites that allow only public
                (unauthenticated) access. An anticipated
                scenario is a ZEO configuration in which some
                clients allow only public access and other
                clients allow full management.
        """
        
        self._ownerous=ownerous
        self._authenticated=authenticated

    def checkPermission(self, permission, object, context):
        # XXX We aren't really handling multiple principals yet

        principals = { context.user : 1 }
        assigned_roles = {}
        roles = {}
        seen_allow = 0

        # Check the placeful principal permissions and aggregate the
        # Roles in this context
        for c in ContainmentIterator(object):
            ppm = queryAdapter(c, IPrincipalPermissionManager, None, globalContext)
            if ppm is not None: 
                for principal in principals.keys():
                    setting = ppm.getSetting(permission, principal)
                    if setting is Deny:
                        return 0 # Explicit deny on principal
                    elif setting is Allow:
                        return 1 # Explicit allow on principal
                    
            prm = queryAdapter(c, IPrincipalRoleManager, None, globalContext)
            if prm is not None:
                for principal in principals.keys():
                    for role, setting in prm.getRolesForPrincipal(principal):
                        if not (role in roles):
                            roles[role] = 1
                            if setting is Assign:
                                assigned_roles[role] = 1
        
        # now check the global principal permissions
        getSetting = principalPermissionManager.getSetting
        for principal in principals.keys():
            setting = getSetting(permission, principal)
            if setting is Allow:
                return 1 # Explicit allow on global principal
            elif setting is Deny:
                return 0 # Explicit deny on global principal
                                    
        # aggregate global roles
        global_roles = principalRoleManager.getRolesForPrincipal(principal)
        for principal in principals.keys():
            for role, setting in global_roles:
                if not (role in roles):
                    roles[role] = 1
                    if setting is Assign:
                        assigned_roles[role] = 1
                        
        # Check the placeful role permissions, checking anonymous first
        for c in ContainmentIterator(object):
            rpm = queryAdapter(c, IRolePermissionManager, None, globalContext)
            if rpm is not None:
                for role in ['Anonymous'] + assigned_roles.keys():
                    setting = rpm.getSetting(permission, role)
                    if setting is Allow:
                        seen_allow = 1 # Flag allow, but continue processing
                    elif setting is Deny:
                        return 0 # Deny on placeful role permission
                if seen_allow:
                    return 1 # Allow on placeful role permission
            
        # Last, check if there are any global role settings
        getSetting = rolePermissionManager.getSetting
        for principal in principals.keys():
            for role, role_setting in [('Anonymous', Assign)] + global_roles:
                if role_setting is Assign:
                    setting = getSetting(permission, role)
                    if setting == Allow:
                        seen_allow = 1 # Flag allow and continue
                    elif setting == Deny:
                        return 0 # Deny on global role
            if seen_allow:
                return 1 # Allow on global role

        return 0 # Deny by default

zopeSecurityPolicy=ZopeSecurityPolicy()

