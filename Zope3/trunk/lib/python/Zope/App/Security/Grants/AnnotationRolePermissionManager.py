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
"""

$Id: AnnotationRolePermissionManager.py,v 1.1 2002/06/20 15:54:59 jim Exp $
"""

from Zope.ComponentArchitecture import getAdapter
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.Security.IRolePermissionManager import IRolePermissionManager
from Zope.App.Security.Grants.LocalSecurityMap import LocalSecurityMap
from Zope.App.Security.Settings import Allow, Deny, Unset

annotation_key = 'Zope.App.Security.AnnotationRolePermissionManager'

class AnnotationRolePermissionManager:
    """
    provide adapter that manages role permission data in an object attribute
    """

    __implements__ = IRolePermissionManager

    def __init__(self, context):
        self._context = context

    def grantPermissionToRole(self, permission_id, role_id):
        ''' See the interface IRolePermissionManager '''
        rp = self._getRolePermissions(create=1)
        rp.addCell(permission_id, role_id, Allow)
        # probably not needed, as annotations should manage
        # their own persistence
        #self._context._p_changed = 1

    def denyPermissionToRole(self, permission_id, role_id):
        ''' See the interface IRolePermissionManager '''
        rp = self._getRolePermissions(create=1)
        rp.addCell(permission_id, role_id, Deny)
        # probably not needed, as annotations should manage
        # their own persistence
        #self._context._p_changed = 1

    def unsetPermissionFromRole(self, permission_id, role_id):
        ''' See the interface IRolePermissionManager '''
        rp = self._getRolePermissions()
        # Only unset if there is a security map, otherwise, we're done
        if rp:
            rp.delCell(permission_id, role_id)
            # probably not needed, as annotations should manage
            # their own persistence
            #self._context._p_changed = 1

    def getRolesForPermission(self, permission_id):
        '''See interface IRolePermissionMap'''
        rp = self._getRolePermissions()
        if rp:
            return rp.getRow(permission_id)
        else:
            return []

    def getPermissionsForRole(self, role_id):
        '''See interface IRolePermissionMap'''
        rp = self._getRolePermissions()
        if rp:
            return rp.getCol(role_id)
        else:
            return []

    def getRolesAndPermissions(self):
        '''See interface IRolePermissionMap'''
        rp = self._getRolePermissions()
        if rp:
            return rp.getAllCells(role_id)
        else:
            return []

    def getSetting(self, permission_id, role_id):
        '''See interface IRolePermissionMap'''
        rp = self._getRolePermissions()
        if rp:
            return rp.getCell(permission_id, role_id)
        else:
            return Unset

    def _getRolePermissions(self, create=0):
        """Get the role permission map stored in the context, optionally
           creating one if necessary"""
        # need to remove security proxies here, otherwise we enter
        # an infinite loop, becuase checking security depends on
        # getting RolePermissions.
        from Zope.Proxy.ProxyIntrospection import removeAllProxies
        context = removeAllProxies(self._context)
        annotations = getAdapter(context, IAnnotations)
        try:
            return annotations[annotation_key]
        except KeyError:
            if create:
                rp = annotations[annotation_key] = LocalSecurityMap()
                return rp
        return None

