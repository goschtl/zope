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

$Id: PermissionField.py,v 1.1 2002/12/21 19:56:36 stevea Exp $
"""

from Zope.Schema.IField import IValueSet
from Zope.Schema import ValueSet
from Zope.Schema.Exceptions import ValidationError
from Zope.ComponentArchitecture import queryService

class IPermissionField(IValueSet):
    u"""Fields with Permissions as values
    """

class PermissionField(ValueSet):
    __doc__ = IPermissionField.__doc__
    __implements__ = IPermissionField

    def _validate(self, value):
        super(PermissionField, self)._validate(value)
        # XXX I'd like to use getService here, but _validate is called
        #     before the zcml actions are executed, so this gets
        #     called before even the Permissions service is set up.
        service = queryService(self.context, 'Permissions', None)
        if service is None:
            # XXX Permissions service not found, so we can't validate.
            #     Perhaps log some message here.
            pass
        else:
            if service.getPermission(value.getId()) is None:
                raise ValidationError("Unknown permission", value)

