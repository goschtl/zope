##############################################################################
#
# Copyright (c) 2005 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""sharing security policy

$Id$
"""

from zope import interface, component

from zope.app import zapi
from zope.app.security.interfaces import PrincipalLookupError

from zope.security.checker import CheckerPublic
from zope.security.management import system_user
from zope.security.simplepolicies import ParanoidSecurityPolicy
from zope.security.interfaces import ISecurityPolicy
from zope.security.proxy import removeSecurityProxy
from zope.app.security.interfaces import PrincipalLookupError

from zc.sharing import interfaces, sharing

admin_group = 'zc.groups.admin' # TODO: Make this configurable

class CacheEntry:
    pass

class SecurityPolicy(ParanoidSecurityPolicy):
    interface.classProvides(ISecurityPolicy)

    def __init__(self, *args, **kw):
        ParanoidSecurityPolicy.__init__(self, *args, **kw)
        self._cache = {}

    def invalidateCache(self):
        self._cache = {}

    def cache(self, parent):
        cache = self._cache.get(id(parent))
        if cache:
            cache = cache[0]
        else:
            cache = CacheEntry()
            self._cache[id(parent)] = cache, parent
        return cache

    def cachedDecision(self, parent, principal, groups, privilege):
        # Return the decision for a principal and permission

        cache = self.cache(parent)
        try:
            cache_decision = cache.decision
        except AttributeError:
            cache_decision = cache.decision = {}

        cache_decision_prin = cache_decision.get(principal)
        if not cache_decision_prin:
            cache_decision_prin = cache_decision[principal] = {}

        try:
            return cache_decision_prin[privilege]
        except KeyError:
            pass

        sharing = interfaces.IBaseSharing(parent, None)
        if sharing is not None:
            decision = sharing.sharedTo(privilege, groups)
        elif parent is None:
            decision = False
        else:
            parent = removeSecurityProxy(getattr(parent, '__parent__', None))
            decision = self.cachedDecision(
                parent, principal, groups, privilege)


        cache_decision_prin[privilege] = decision
        return decision


    def checkPermission(self, permission, object):
        if permission is CheckerPublic:
            return True

        object = removeSecurityProxy(object)
        seen = {}
        for participation in self.participations:
            principal = participation.principal
            if principal is system_user:
                continue # always allow system_user

            if principal.id in seen or principal.id in systemAdministrators:
                continue


            groups = self._groupsFor(principal)

            privilege = _permissionPrivileges.get(permission, -1)
            if privilege < 0:
                # No privilege
                return False

            if admin_group not in groups:
                # admins have all privileges:

                if not self.cachedDecision(
                    object, principal.id, groups, privilege,
                    ):
                    return False

            seen[principal.id] = 1

        return True

    def _groupsFor(self, principal):
        groups = self._cache.get(principal.id)
        if groups is None:
            groups = getattr(principal, 'groups', ())
            if groups:
                groups = {}
                getPrincipal = zapi.principals().getPrincipal
                _findGroupsFor(principal, getPrincipal, groups)
            else:
                groups = {}

            groups[principal.id] = 1

            self._cache[principal.id] = groups

        return groups

def _findGroupsFor(principal, getPrincipal, seen):
    for group_id in getattr(principal, 'groups', ()):
        if group_id in seen:
            # Dang, we have a cycle.  We don't want to
            # raise an exception here (or do we), so we'll skip it
            continue
        seen[group_id] = 1

        try:
            group = getPrincipal(group_id)
        except PrincipalLookupError:
            # It's bad if we have an undefined principal,
            # but we don't want to fail here.  But we won't
            # honor any grants for the group. We'll just skip it.
            continue

        _findGroupsFor(group, getPrincipal, seen)

_permissionPrivileges = {}
permissionPrivilege = _permissionPrivileges.__setitem__
getPermissionPrivilege = _permissionPrivileges.__getitem__
removePermissionPrivilege = _permissionPrivileges.__delitem__

def fixedAdapter(adapter):

    def adapt(ob):
        return adapter

    return adapt

class SharingPrivileges:
    interface.implements(interfaces.ISharingPrivileges)

    def __init__(self, privileges):
        self.privileges = tuple(privileges)

def sharingPrivileges(for_, titles):
    defined = dict([(p['title'], p) for p in sharing.getPrivileges()])

    ids = []
    for title in titles:
        try:
            ids.append(defined[title]['id'])
        except KeyError:
            raise ValueError("Undefined privilege", title)

    component.provideAdapter(fixedAdapter(SharingPrivileges(ids)),
                             (for_, ), interfaces.ISharingPrivileges)

class SubobjectSharingPrivileges:
    interface.implements(interfaces.ISharingPrivileges)

    def __init__(self, privileges):
        self.subobjectPrivileges = tuple(privileges)

def subobjectSharingPrivileges(for_, titles):
    defined = dict([(p['title'], p) for p in sharing.getPrivileges()])

    ids = []
    for title in titles:
        try:
            ids.append(defined[title]['id'])
        except KeyError:
            raise ValueError("Undefined privilege", title)

    component.provideAdapter(fixedAdapter(SubobjectSharingPrivileges(ids)),
                             (for_, ), interfaces.ISubobjectSharingPrivileges)

systemAdministrators = ()
