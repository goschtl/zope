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
"""Define Zope's default security policy

$Id$"""


# AccessControl.Implementation inserts ZopeSecurityPolicy, getRoles
from AccessControl.SimpleObjectPolicies import _noroles

rolesForPermissionOn = None  # XXX:  avoid import loop

tuple_or_list = tuple, list

def getRoles(container, name, value, default):

    global rolesForPermissionOn  # XXX:  avoid import loop

    if rolesForPermissionOn is None:
        from PermissionRole import rolesForPermissionOn

    roles = getattr(value, '__roles__', _noroles)
    if roles is _noroles:
        if not name or not isinstance(name, basestring):
            return default

        cls = getattr(container, '__class__', None)
        if cls is None:
            return default
        
        roles = getattr(cls, name+'__roles__', _noroles)
        if roles is _noroles:
            return default

        value = container

    if roles is None or isinstance(roles, tuple_or_list):
        return roles
    
    rolesForPermissionOn = getattr(roles, 'rolesForPermissionOn', None)
    if rolesForPermissionOn is not None:
        roles = rolesForPermissionOn(value)

    return roles
