##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
""" Some common utilities.

$Id$
"""

import os
from App.Common import package_home

_dtmldir = os.path.join( package_home( globals() ), 'dtml' )

from AccessControl.Role import gather_permissions
from AccessControl.Permission import Permission

def ac_inherited_permissions(ob, all=0):
    # Get all permissions not defined in ourself that are inherited
    # This will be a sequence of tuples with a name as the first item and
    # an empty tuple as the second.
    d = {}
    perms = getattr(ob, '__ac_permissions__', ())
    for p in perms: d[p[0]] = None
    r = gather_permissions(ob.__class__, [], d)
    if all:
       if hasattr(ob, '_subobject_permissions'):
           for p in ob._subobject_permissions():
               pname=p[0]
               if not d.has_key(pname):
                   d[pname]=1
                   r.append(p)
       r = list(perms) + r
    return r

def modifyRolesForPermission(ob, pname, roles):
    '''
    Modifies multiple role to permission mappings.  roles is a list to
    acquire, a tuple to not acquire.
    '''
    # This mimics what AccessControl/Role.py does.
    data = ()
    for perm in ac_inherited_permissions(ob, 1):
        name, value = perm[:2]
        if name == pname:
            data = value
            break
    p = Permission(pname, data, ob)
    if p.getRoles() != roles:
        p.setRoles(roles)
        return 1
    return 0

def modifyRolesForGroup(ob, group, grant_roles, managed_roles):
    """Modifies local roles for one group.
    """
    moniker = "(Group) %s" % group
    local_roles = getattr(ob, '__ac_local_roles__', None)
    if local_roles is None:
        local_roles = {}
    roles = local_roles.get(moniker)
    if not roles:
        if not grant_roles:
            # No roles exist and no grants requested.  Leave unchanged.
            return 0
        else:
            # Add new roles for this group.
            local_roles[moniker] = list(grant_roles)
            ob.__ac_local_roles__ = local_roles
            return 1
    # Edit the roles.
    roles = list(roles)
    changed = 0
    for role in managed_roles:
        if role in grant_roles and role not in roles:
            # Add one role for this group.
            roles.append(role)
            changed = 1
        elif role not in grant_roles and role in roles:
            # Remove one role for this group.
            roles.remove(role)
            changed = 1
    if changed:
        if not roles and local_roles.has_key(moniker):
            del local_roles[moniker]
        else:
            local_roles[moniker] = roles
        ob.__ac_local_roles__ = local_roles
    return changed

def modifyExpandedGroups(ob, group, grant_roles, managed_roles):
    """Modifies local roles for a group.

    The group may expand into multiple groups as defined by a
    context-sensitive aggregated group mapping.
    """
    groups = [group]
    if hasattr(ob, "__group_mapping__"):
        map = ob.getAggregatedGroupMapping()
        expanded = map.get(group)
        if expanded:
            groups = expanded
    changed = 0
    for g in groups:
        if modifyRolesForGroup(ob, g, grant_roles, managed_roles):
            changed = 1
    return changed
