##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Permissions

$Id$
"""
from zope.interface import implements
from zope.schema.interfaces import ValidationError
from zope.security.checker import CheckerPublic
from zope.app import zapi
from zope.app.security.interfaces import IPermission


class Permission(object):
    implements(IPermission)

    def __init__(self, id, title="", description=""):
        self.id = id
        self.title = title
        self.description = description


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
    if permission_id is CheckerPublic:
        return
    if not zapi.queryUtility(IPermission, permission_id, context=context):
        raise ValueError("Undefined permission id", permission_id)

def allPermissions(context=None):
    """Get the ids of all defined permissions

    >>> from zope.app.tests.placelesssetup import setUp, tearDown
    >>> setUp()

    >>> from zope.app.tests.ztapi import provideUtility
    >>> provideUtility(IPermission, Permission('x'), 'x')
    >>> provideUtility(IPermission, Permission('y'), 'y')

    >>> ids = list(allPermissions(None))
    >>> ids.sort()
    >>> ids
    [u'x', u'y']

    >>> tearDown()
    """
    for id, permission in zapi.getUtilitiesFor(IPermission, context):
        if id != u'zope.Public':
            yield id
