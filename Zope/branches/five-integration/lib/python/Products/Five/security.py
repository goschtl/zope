##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Five security handling

$Id: security.py 8281 2005-01-14 18:20:18Z regebro $
"""
from zope.interface import implements
from zope.component import queryUtility, getUtility
from zope.app.security.interfaces import IPermission
from zope.app import zapi

from AccessControl import ClassSecurityInfo, getSecurityManager
from Globals import InitializeClass
from types import StringTypes

CheckerPublicId = 'zope.Public'
CheckerPrivateId = 'zope2.Private'
from zope.security.checker import CheckerPublic

def getSecurityInfo(klass):
    sec = {}
    info = vars(klass)
    if info.has_key('__ac_permissions__'):
        sec['__ac_permissions__'] = info['__ac_permissions__']
    for k, v in info.items():
        if k.endswith('__roles__'):
            sec[k] = v
    return sec

def clearSecurityInfo(klass):
    sec = {}
    info = vars(klass)
    if info.has_key('__ac_permissions__'):
        delattr(klass, '__ac_permissions__')
    for k, v in info.items():
        if k.endswith('__roles__'):
            delattr(klass, k)

def checkPermission(permission, object, interaction=None):
    """Return whether security policy allows permission on object.

    Arguments:
    permission -- A permission name
    object -- The object being accessed according to the permission
    interaction -- This Zope 3 concept has no equivalent in Zope 2,
        and is ignored.

    checkPermission is guaranteed to return True if permission is
    CheckerPublic or None.
    """

    if (permission in ('zope.Public', 'zope2.Public') or
        permission is None or permission is CheckerPublic):
        return True

    if isinstance(permission, StringTypes):
        permission = zapi.queryUtility(IPermission, unicode(permission))
        if permission is None:
            return False

    if getSecurityManager().checkPermission(permission.title, object):
        return True

    return False

def initializeClass(klass):
    InitializeClass(klass)

def _getSecurity(klass):
    # a Zope 2 class can contain some attribute that is an instance
    # of ClassSecurityInfo. Zope 2 scans through things looking for
    # an attribute that has the name __security_info__ first
    info = vars(klass)
    for k, v in info.items():
        if hasattr(v, '__security_info__'):
            return v
    # we stuff the name ourselves as __security__, not security, as this
    # could theoretically lead to name clashes, and doesn't matter for
    # zope 2 anyway.
    security = ClassSecurityInfo()
    setattr(klass, '__security__', security)
    return security

def protectName(klass, name, permission_id):
    """Protect the attribute 'name' on 'klass' using the given
       permission"""
    security = _getSecurity(klass)
    # XXX: Sometimes, the object CheckerPublic is used instead of the
    # string zope.Public. I haven't ben able to figure out why, or if
    # it is correct, or a bug. So this is a workaround.
    if permission_id is CheckerPublic:
        security.declarePublic(name)
        return
    # Zope 2 uses string, not unicode yet
    name = str(name)
    if permission_id == CheckerPublicId:
        security.declarePublic(name)
    elif permission_id == CheckerPrivateId:
        security.declarePrivate(name)
    else:
        permission = getUtility(IPermission, name=permission_id)
        # Zope 2 uses string, not unicode yet
        perm = str(permission.title)
        security.declareProtected(perm, name)

def protectClass(klass, permission_id):
    """Protect the whole class with the given permission"""
    security = _getSecurity(klass)
    if permission_id == CheckerPublicId:
        security.declareObjectPublic()
    elif permission_id == CheckerPrivateId:
        security.declareObjectPrivate()
    else:
        permission = getUtility(IPermission, name=permission_id)
        # Zope 2 uses string, not unicode yet
        perm = str(permission.title)
        security.declareObjectProtected(perm)
