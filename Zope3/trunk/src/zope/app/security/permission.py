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

$Id: permission.py,v 1.2 2003/01/21 21:21:46 jim Exp $
"""

from zope.schema import ValueSet
from zope.schema.interfaces import ValidationError
from zope.component import getService
from zope.app.interfaces.security import IPermissionField


def checkPermission(context, permission_id):
    
    if not getService(context, 'Permissions').getPermission(permission_id):
        raise ValueError("Undefined permission id", permission_id)

class PermissionField(ValueSet):
    __doc__ = IPermissionField.__doc__
    __implements__ = IPermissionField

    def _validate(self, value):
        super(PermissionField, self)._validate(value)
        service = getService(self.context, 'Permissions')
        if service.getPermission(value) is None:
            raise ValidationError("Unknown permission", value)
