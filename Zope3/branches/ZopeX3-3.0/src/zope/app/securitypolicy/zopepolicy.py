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
"""Define Zope's default security policy

$Id$
"""

import zope.interface

from zope.security.management import system_user
from zope.security.simplepolicies import ParanoidSecurityPolicy
from zope.security.interfaces import ISecurityPolicy
from zope.security.proxy import removeSecurityProxy

from zope.app.security.settings import Allow, Deny

from zope.app.securitypolicy.principalpermission \
     import principalPermissionManager
globalPrincipalPermissionSetting = principalPermissionManager.getSetting

from zope.app.securitypolicy.rolepermission import rolePermissionManager
globalRolesForPermission = rolePermissionManager.getRolesForPermission

from zope.app.securitypolicy.principalrole import principalRoleManager
globalRolesForPrincipal = principalRoleManager.getRolesForPrincipal

from zope.app.securitypolicy.interfaces import IRolePermissionMap
from zope.app.securitypolicy.interfaces import IPrincipalPermissionMap
from zope.app.securitypolicy.interfaces import IPrincipalRoleMap
from zope.app.securitypolicy.interfaces import IGrantInfo

class CacheEntry:
    pass
    
class ZopeSecurityPolicy(ParanoidSecurityPolicy):
    zope.interface.classProvides(ISecurityPolicy)

    def __init__(self, *args, **kw):
        ParanoidSecurityPolicy.__init__(self, *args, **kw)
        self._cache = {}

    def invalidate_cache(self):
        self._cache = {}

    def cache(self, parent):
        cache = self._cache.get(id(parent))
        if cache:
            cache = cache[0]
        else:
            cache = CacheEntry()
            self._cache[id(parent)] = cache, parent
        return cache
    
    def cached_decision(self, parent, principal, permission):
        cache = self.cache(parent)
        try:
            cache_decision = cache.decision
        except AttributeError:
            cache_decision = cache.decision = {}

        cache_decision_prin = cache_decision.get(principal)
        if not cache_decision_prin:
            cache_decision_prin = cache_decision[principal] = {}
            
        try:
            return cache_decision_prin[permission]
        except KeyError:
            pass
            
        decision = self.cached_prinper(parent, principal, permission)
        if decision is not None:
            cache_decision_prin[permission] = decision
            return decision

        roles = self.cached_roles(parent, permission)
        if roles:
            for role in self.cached_principal_roles(parent, principal):
                if role in roles:
                    cache_decision_prin[permission] = decision = True
                    return decision

        cache_decision_prin[permission] = decision = False
        return decision
        
    def cached_prinper(self, parent, principal, permission):
        cache = self.cache(parent)
        try:
            cache_prin = cache.prin
        except AttributeError:
            cache_prin = cache.prin = {}

        cache_prin_per = cache_prin.get(principal)
        if not cache_prin_per:
            cache_prin_per = cache_prin[principal] = {}

        try:
            return cache_prin_per[permission]
        except KeyError:
            pass

        if parent is None:
            prinper = globalPrincipalPermissionSetting(
                permission, principal, None)
            if prinper is not None:
                prinper = prinper is Allow
            cache_prin_per[permission] = prinper
            return prinper

        prinper = IPrincipalPermissionMap(parent, None)
        if prinper is not None:
            prinper = prinper.getSetting(permission, principal, None)
            if prinper is not None:
                prinper = prinper is Allow
                cache_prin_per[permission] = prinper
                return prinper

        parent = removeSecurityProxy(getattr(parent, '__parent__', None))
        prinper = self.cached_prinper(parent, principal, permission)
        cache_prin_per[permission] = prinper
        return prinper
        
    def cached_roles(self, parent, permission):
        cache = self.cache(parent)
        try:
            cache_roles = cache.roles
        except AttributeError:
            cache_roles = cache.roles = {}
        try:
            return cache_roles[permission]
        except KeyError:
            pass
        
        if parent is None:
            roles = dict(
                [(role, 1)
                 for (role, setting) in globalRolesForPermission(permission)
                 if setting is Allow
                 ]
               )
            cache_roles[permission] = roles
            return roles

        roles = self.cached_roles(
            removeSecurityProxy(getattr(parent, '__parent__', None)),
            permission)
        roleper = IRolePermissionMap(parent, None)
        if roleper:
            roles = roles.copy()
            for role, setting in roleper.getRolesForPermission(permission):
                if setting is Allow:
                    roles[role] = 1
                elif role in roles:
                    del roles[role]

        cache_roles[permission] = roles
        return roles

    def cached_principal_roles(self, parent, principal):
        cache = self.cache(parent)
        try:
            cache_principal_roles = cache.principal_roles
        except AttributeError:
            cache_principal_roles = cache.principal_roles = {}
        try:
            return cache_principal_roles[principal]
        except KeyError:
            pass

        if parent is None:
            roles = dict(
                [(role, 1)
                 for (role, setting) in globalRolesForPrincipal(principal)
                 if setting is Allow
                 ]
                 )
            roles['zope.Anonymous'] = 1 # Everybody has Anonymous
            cache_principal_roles[principal] = roles
            return roles
            
        roles = self.cached_principal_roles(
            removeSecurityProxy(getattr(parent, '__parent__', None)),
            principal)
        prinrole = IPrincipalRoleMap(parent, None)
        if prinrole:
            roles = roles.copy()
            for role, setting in prinrole.getRolesForPrincipal(principal):
                if setting is Allow:
                    roles[role] = 1
                elif role in roles:
                    del roles[role]

        cache_principal_roles[principal] = roles
        return roles
        

    def checkPermission(self, permission, object):
        principals = {}
        for participation in self.participations:
            principal = participation.principal
            if principal is system_user:
                continue # always allow system_user
            principals[principal.id] = 1

        if not principals:
            return True

        object = removeSecurityProxy(object)
        parent = removeSecurityProxy(getattr(object, '__parent__', None))

        grant_info = IGrantInfo(object, None)
        if not grant_info:
            # No local grants; just use cached decision for parent
            for principal in principals:
                if not self.cached_decision(parent, principal, permission):
                    return False
            return True

        # We need to combine local and parent info
            
        # First, look for principal grants
        for principal in principals.keys():
            setting = grant_info.principalPermissionGrant(
                principal, permission)
            if setting is Deny:
                return False
            elif setting is Allow: # setting could be None
                del principals[principal]
                if not principals:
                    return True
                continue

            decision = self.cached_prinper(parent, principal, permission)
            if decision is not None:
                if decision:
                    del principals[principal]
                    if not principals:
                        return True
                else:
                    return decision # False

        roles = self.cached_roles(parent, permission)
        local_roles = grant_info.getRolesForPermission(permission)
        if local_roles:
            roles = roles.copy()
            for role, setting in local_roles:
                if setting is Allow:
                    roles[role] = 1
                elif role in roles:
                    del roles[role]

        for principal in principals.keys():
            proles = self.cached_principal_roles(parent, principal).copy()
            for role, setting in grant_info.getRolesForPrincipal(principal):
                if setting is Allow:
                    if role in roles:
                        del principals[principal]
                        if not principals:
                            return True
                        break
                elif role in proles:
                    del proles[role]
            else:
                for role in proles:
                    if role in roles:
                        del principals[principal]
                        if not principals:
                            return True
                        break                        
                
        return False

