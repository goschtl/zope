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
"""These are the interfaces for the common fields.

$Id: permission.py,v 1.7 2003/04/14 18:21:36 fdrake Exp $
"""

from zope.schema import Enumerated, Field
from zope.schema.interfaces import ValidationError
from zope.component import getService
from zope.app.services.servicenames import Permissions
from zope.app.interfaces.security import IPermissionField
from zope.security.checker import CheckerPublic


def checkPermission(context, permission_id):
    
    if not getService(context, Permissions).getPermission(permission_id):
        raise ValueError("Undefined permission id", permission_id)

class PermissionField(Enumerated, Field):
    __doc__ = IPermissionField.__doc__
    __implements__ = IPermissionField

    def _validate(self, value):
        if value is CheckerPublic:
            return
        super(PermissionField, self)._validate(value)
        service = getService(self.context, Permissions)
        if service.getPermission(value) is None:
            raise ValidationError("Unknown permission", value)
