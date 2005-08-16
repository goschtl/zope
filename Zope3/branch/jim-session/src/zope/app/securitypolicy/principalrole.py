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
"""Mappings between principals and roles, stored in an object locally."""

__metaclass__ = type

from zope.interface import implements
from zope.security.proxy import trustedRemoveSecurityProxy

from zope.app.annotation.interfaces import IAnnotations
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager
from zope.app.securitypolicy.interfaces import IPrincipalRoleMap

from zope.app.security.settings import Allow, Deny, Unset
from zope.app.securitypolicy.securitymap import SecurityMap
from zope.app.securitypolicy.securitymap import PersistentSecurityMap

from zope.app.security.principal import checkPrincipal
from zope.app.securitypolicy.role import checkRole

annotation_key = 'zope.app.security.AnnotationPrincipalRoleManager'

class AnnotationPrincipalRoleManager:
    """Mappings between principals and roles."""

    implements(IPrincipalRoleManager)

    def __init__(self, context):
        self._context = context

    def assignRoleToPrincipal(self, role_id, principal_id):
        ''' See the interface IPrincipalRoleManager '''
        pp = self._getPrincipalRoles(create=1)
        pp.addCell(role_id, principal_id, Allow)

    def removeRoleFromPrincipal(self, role_id, principal_id):
        ''' See the interface IPrincipalRoleManager '''
        pp = self._getPrincipalRoles(create=1)
        pp.addCell(role_id, principal_id, Deny)

    def unsetRoleForPrincipal(self, role_id, principal_id):
        ''' See the interface IPrincipalRoleManager '''
        pp = self._getPrincipalRoles()
        # Only unset if there is a security map, otherwise, we're done
        if pp:
            pp.delCell(role_id, principal_id)

    def getPrincipalsForRole(self, role_id):
        ''' See the interface IPrincipalRoleManager '''
        pp = self._getPrincipalRoles()
        if pp:
            return pp.getRow(role_id)
        return []

    def getRolesForPrincipal(self, principal_id):
        ''' See the interface IPrincipalRoleManager '''
        pp = self._getPrincipalRoles()
        if pp:
            return pp.getCol(principal_id)
        return []

    def getSetting(self, role_id, principal_id):
        ''' See the interface IPrincipalRoleManager '''
        pp = self._getPrincipalRoles()
        if pp:
            return pp.getCell(role_id, principal_id, default=Unset)
        return Unset

    def getPrincipalsAndRoles(self):
        ''' See the interface IPrincipalRoleManager '''
        pp = self._getPrincipalRoles()
        if pp:
            return pp.getAllCells()
        return []

    # Implementation helpers

    def _getPrincipalRoles(self, create=0):
        """ Get the principal role map stored in the context, optionally
            creating one if necessary """
        annotations = IAnnotations(self._context)
        try:
            # there's a chance that annotations is security proxied -
            # remove proxy to avoid authentication failure on role lookup
            return trustedRemoveSecurityProxy(annotations)[annotation_key]
        except KeyError:
            if create:
                rp = annotations[annotation_key] = PersistentSecurityMap()
                return rp
        return None


class PrincipalRoleManager(SecurityMap):
    """Mappings between principals and roles."""

    implements(IPrincipalRoleManager, IPrincipalRoleMap)

    def assignRoleToPrincipal(self, role_id, principal_id, check=True):
        ''' See the interface IPrincipalRoleManager '''

        if check:
            checkPrincipal(None, principal_id)
            checkRole(None, role_id)

        self.addCell(role_id, principal_id, Allow)

    def removeRoleFromPrincipal(self, role_id, principal_id, check=True):
        ''' See the interface IPrincipalRoleManager '''

        if check:
            checkPrincipal(None, principal_id)
            checkRole(None, role_id)

        self.addCell(role_id, principal_id, Deny)

    def unsetRoleForPrincipal(self, role_id, principal_id):
        ''' See the interface IPrincipalRoleManager '''

        # Don't check validity intentionally.
        # After all, we certianly want to unset invalid ids.

        self.delCell(role_id, principal_id)

    def getPrincipalsForRole(self, role_id):
        ''' See the interface IPrincipalRoleMap '''
        return self.getRow(role_id)

    def getRolesForPrincipal(self, principal_id):
        ''' See the interface IPrincipalRoleMap '''
        return self.getCol(principal_id)

    def getSetting(self, role_id, principal_id):
        ''' See the interface IPrincipalRoleMap '''
        return self.getCell(role_id, principal_id, default=Unset)

    def getPrincipalsAndRoles(self):
        ''' See the interface IPrincipalRoleMap '''
        return self.getAllCells()

# Roles are our rows, and principals are our columns
principalRoleManager = PrincipalRoleManager()

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(principalRoleManager._clear)
del addCleanUp
