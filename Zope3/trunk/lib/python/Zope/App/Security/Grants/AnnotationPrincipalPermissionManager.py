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
"""Mappings between principals and permissions, stored in an object locally."""

from Zope.ComponentArchitecture import getAdapter
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.Security.IPrincipalPermissionManager \
     import IPrincipalPermissionManager
from Zope.App.Security.Grants.LocalSecurityMap import LocalSecurityMap
from Zope.App.Security.Settings import Allow, Deny, Unset

annotation_key = 'Zope.App.Security.AnnotationPrincipalPermissionManager'

class AnnotationPrincipalPermissionManager:
    """Mappings between principals and permissions."""

    __implements__ = IPrincipalPermissionManager

    def __init__(self, context):
        self._context = context

    def grantPermissionToPrincipal(self, permission_id, principal_id):
        ''' See the interface IPrincipalPermissionManager '''
        pp = self._getPrincipalPermissions(create=1)
        pp.addCell(permission_id, principal_id, Allow)
        self._context._p_changed = 1

    def denyPermissionToPrincipal(self, permission_id, principal_id):
        ''' See the interface IPrincipalPermissionManager '''
        pp = self._getPrincipalPermissions(create=1)
        pp.addCell(permission_id, principal_id, Deny)
        self._context._p_changed = 1

    def unsetPermissionForPrincipal(self, permission_id, principal_id):
        ''' See the interface IPrincipalPermissionManager '''
        pp = self._getPrincipalPermissions()
        # Only unset if there is a security map, otherwise, we're done
        if pp:
            pp.delCell(permission_id, principal_id)
            self._context._p_changed = 1

    def getPrincipalsForPermission(self, permission_id):
        ''' See the interface IPrincipalPermissionManager '''
        pp = self._getPrincipalPermissions()
        if pp: 
            return pp.getRow(permission_id)
        return []

    def getPermissionsForPrincipal(self, principal_id):
        ''' See the interface IPrincipalPermissionManager '''
        pp = self._getPrincipalPermissions()
        if pp: 
            return pp.getCol(principal_id)
        return []

    def getSetting(self, permission_id, principal_id):
        ''' See the interface IPrincipalPermissionManager '''
        pp = self._getPrincipalPermissions()
        if pp: 
            return pp.getCell(permission_id, principal_id, default=Unset)
        return []

    def getPrincipalsAndPermissions(self):
        ''' See the interface IPrincipalPermissionManager '''
        pp = self._getPrincipalPermissions()
        if pp: 
            return pp.getAllCells()
        return []

    # Implementation helpers

    def _getPrincipalPermissions(self, create=0):
        """ Get the principal permission map stored in the context, optionally
            creating one if necessary """
        # need to remove security proxies here, otherwise we enter
        # an infinite loop, becuase checking security depends on
        # getting PrincipalPermissions.
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
