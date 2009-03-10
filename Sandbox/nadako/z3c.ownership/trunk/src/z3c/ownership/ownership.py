##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Ownership implementation

$Id$
"""
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError
from zope.component import adapts, getUtility
from zope.event import notify
from zope.interface import implements
from zope.security.interfaces import IPrincipal
from zope.securitypolicy.interfaces import IPrincipalRoleMap, IPrincipalRoleManager, Allow
from zope.proxy import sameProxiedObjects

from z3c.ownership.interfaces import IOwnerAware, IOwnership, OwnerChangedEvent
from z3c.ownership.interfaces import OWNER_ROLE

class Ownership(object):
    
    adapts(IOwnerAware)
    implements(IOwnership)
    
    def __init__(self, context):
        self._rolemanager = IPrincipalRoleManager(context)
        self.context = context

    def _getCurrentOwnerId(self):
        settings = self._rolemanager.getPrincipalsForRole(OWNER_ROLE)
        principals = [principal_id for (principal_id, setting) in settings if sameProxiedObjects(setting, Allow)]
        if not principals:
            return None
        if len(principals) > 1:
            raise RuntimeError('Object has multiple owners. This should not happen')
        return principals[0]
        
    @apply
    def owner():

        def fget(self):
            principal_id = self._getCurrentOwnerId()
            if principal_id is None:
                return None
            try:
                return getUtility(IAuthentication).getPrincipal(principal_id)
            except PrincipalLookupError:
                return None
        
        def fset(self, new_owner):
            if not (new_owner is None or IPrincipal.providedBy(new_owner)):
                raise ValueError('IPrincipal object or None required')

            if new_owner is None:
                new_owner_id = None
            else:
                new_owner_id = new_owner.id

            current_owner_id = self._getCurrentOwnerId()

            if new_owner_id == current_owner_id:
                return

            if current_owner_id is not None:
                self._rolemanager.unsetRoleForPrincipal(OWNER_ROLE, current_owner_id)
                current_owner = getUtility(IAuthentication).getPrincipal(current_owner_id)
            else:
                current_owner = None

            if new_owner_id:
                self._rolemanager.assignRoleToPrincipal(OWNER_ROLE, new_owner_id)

            notify(OwnerChangedEvent(self.context, new_owner, current_owner))
            
        return property(fget, fset)
