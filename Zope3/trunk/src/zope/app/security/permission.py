##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Permissions

$Id: permission.py,v 1.11 2004/03/08 12:06:01 srichter Exp $
"""
from zope.interface import implements
from zope.schema import Enumerated, Field
from zope.schema.interfaces import ValidationError
from zope.security.checker import CheckerPublic
from zope.app import zapi
from interfaces import IPermission, IPermissionField


class Permission(object):
    implements(IPermission)

    def __init__(self, id, title="", description=""):
        self.id = id
        self.title = title
        self.description = description


def checkPermission(context, permission_id):
    """Check whether a given permission exists in the provided context."""
    if permission_id == CheckerPublic:
        return
    if not zapi.queryUtility(context, IPermission, name=permission_id):
        raise ValueError("Undefined permission id", permission_id)


class PermissionField(Enumerated, Field):
    """A field that represents a permission in a schema"""
    implements(IPermissionField)

    def _validate(self, value):
        if value is CheckerPublic:
            return
        super(PermissionField, self)._validate(value)
        if zapi.queryUtility(self.context, IPermission, name=value) is None:
            raise ValidationError("Unknown permission", value)


def _addCheckerPublic():
    """Add the CheckerPublic permission as 'zope.Public'"""
    from zope.component.utility import utilityService
    perm = Permission('zope.Public', 'Public',
            """Special permission used for resources that are always public

            The public permission is effectively an optimization, sine
            it allows security computation to be bypassed.
            """
            )
    utilityService.provideUtility(IPermission, perm, perm.id)

_addCheckerPublic()

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_addCheckerPublic)
del addCleanUp
