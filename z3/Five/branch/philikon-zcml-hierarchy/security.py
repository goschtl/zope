##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Five security handling

$Id$
"""
from zope.interface import implements
from zope.component import queryUtility, getUtility
from zope.app.security.interfaces import IPermission

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

CheckerPublic = 'zope.Public'
CheckerPrivate = 'zope.Private'

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

def checkPermission(context, permission_id):
    """Check whether a given permission exists in the provided context.

    >>> from zope.app.tests.placelesssetup import setUp, tearDown
    >>> setUp()

    >>> from zope.app.tests.ztapi import provideUtility
    >>> provideUtility(IPermission, Permission('x'), 'x')

    >>> checkPermission(None, 'x')
    >>> checkPermission(None, 'y')
    Traceback (most recent call last):
    ...
    ValueError: ('Undefined permission id', 'y')

    >>> tearDown()
    """
    if permission_id == CheckerPublic:
        return
    if not queryUtility(IPermission, permission_id, context=context):
        raise ValueError("Undefined permission id", permission_id)

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
    # Zope 2 uses string, not unicode yet
    name = str(name)
    if permission_id == CheckerPublic:
        security.declarePublic(name)
    elif permission_id == CheckerPrivate:
        security.declarePrivate(name)
    else:
        permission = getUtility(IPermission, name=permission_id)
        # Zope 2 uses string, not unicode yet
        perm = str(permission.title)
        security.declareProtected(perm, name)

def protectClass(klass, permission_id):
    """Protect the whole class with the given permission"""
    security = _getSecurity(klass)
    if permission_id == CheckerPublic:
        security.declareObjectPublic()
    elif permission_id == CheckerPrivate:
        security.declareObjectPrivate()
    else:
        permission = getUtility(IPermission, name=permission_id)
        # Zope 2 uses string, not unicode yet
        perm = str(permission.title)
        security.declareObjectProtected(perm)
