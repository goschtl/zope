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

$Id: permission.py,v 1.10 2004/02/24 14:12:11 srichter Exp $
"""
from zope.schema import Enumerated, Field
from zope.schema.interfaces import ValidationError
from zope.component import getService
from zope.app.services.servicenames import Permissions
from zope.app.interfaces.security import IPermissionField
from zope.security.checker import CheckerPublic
from zope.interface import implements


def checkPermission(context, permission_id):
    """Check whether a given permission exists in the provided context."""
    if not getService(context, Permissions).getPermission(permission_id):
        raise ValueError("Undefined permission id", permission_id)


class PermissionField(Enumerated, Field):
    """A field that represents a permission in a schema"""
    implements(IPermissionField)

    def _validate(self, value):
        if value is CheckerPublic:
            return
        super(PermissionField, self)._validate(value)
        service = getService(self.context, Permissions)
        if service.getPermission(value) is None:
            raise ValidationError("Unknown permission", value)
