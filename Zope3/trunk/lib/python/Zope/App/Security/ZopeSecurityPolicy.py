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

$Id: ZopeSecurityPolicy.py,v 1.4 2002/07/02 19:48:38 jim Exp $
"""
__version__='$Revision: 1.4 $'[11:-2]

from Zope.ComponentArchitecture import queryAdapter
from Zope.Proxy.ContextWrapper import ContainmentIterator
from Zope.Exceptions import Unauthorized, Forbidden
from Zope.Security.ISecurityPolicy import ISecurityPolicy
from Zope.App.Security.IRolePermissionManager \
     import IRolePermissionManager, IRolePermissionMap
from Zope.App.Security.IPrincipalPermissionManager \
    import IPrincipalPermissionManager, IPrincipalPermissionMap
from Zope.App.Security.IPrincipalRoleManager \
    import IPrincipalRoleManager, IPrincipalRoleMap
from Zope.App.Security.IRolePermissionManager import IRolePermissionManager
from Zope.App.Security.Registries.PermissionRegistry import permissionRegistry 
from Zope.App.Security.Registries.PrincipalRegistry import principalRegistry 
from Zope.App.Security.Registries.RoleRegistry import roleRegistry
from Zope.App.Security.Grants.Global.PrincipalPermissionManager \
     import principalPermissionManager 
from Zope.App.Security.Grants.Global.RolePermissionManager \
     import rolePermissionManager 
from Zope.App.Security.Grants.Global.PrincipalRoleManager \
     import principalRoleManager
from Zope.App.Security.Settings import Allow, Deny

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
            ppm = queryAdapter(c, IPrincipalPermissionManager, None,
                               globalContext)
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
                            if setting is Allow:
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
                    if setting is Allow:
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
            for role, role_setting in [('Anonymous', Allow)] + global_roles:
                if role_setting is Allow:
                    setting = getSetting(permission, role)
                    if setting == Allow:
                        seen_allow = 1 # Flag allow and continue
                    elif setting == Deny:
                        return 0 # Deny on global role
            if seen_allow:
                return 1 # Allow on global role

        return 0 # Deny by default



def permissionsOfPrincipal(principal, object):
    permissions = {}
    roles = {'Anonymous': Allow} # Everyone has anonymous
    role_permissions = {}
    orig = object

    # Make two passes.

    # First, collect what we know about the principal:
    for object in ContainmentIterator(orig):

        # Copy specific principal permissions
        prinper = queryAdapter(object, IPrincipalPermissionMap)
        if prinper is not None:
            for permission, setting in prinper.getPermissionsForPrincipal(
                principal):
                if permission not in permissions:
                    permissions[permission] = setting

        # Collect principal roles
        prinrole = queryAdapter(object, IPrincipalRoleMap)
        if prinrole is not None:
            for role, setting in prinrole.getRolesForPrincipal(principal):
                if role not in roles:
                    roles[role] = setting

    # get global principal permissions
    for permission, setting in getPermissionsForPrincipal(principal):
        if permission not in permissions:
            permissions[permission] = setting

    # get glolbal principal roles
    for role, setting in getRolesForPrincipal(principal):
        if role not in roles:
            roles[role] = setting

    # Second, update permissions using principal 
    for object in ContainmentIterator(orig):

        # Collect role permissions
        roleper = queryAdapter(object, IRolePermissionMap)
        if roleper is not None:
            for perm, role, setting in roleper.getRolesAndPermissions():
                if role in roles and perm not in permissions:
                    permissions[perm] = setting


    for perm, role, setting in (
        rolePermissionManager.getRolesAndPermissions()):
        if role in roles and perm not in permissions:
            permissions[perm] = setting


    result = [permission
              for permission in permissions
              if permissions[permission] is Allow]

    return result



zopeSecurityPolicy=ZopeSecurityPolicy()

