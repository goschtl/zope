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
"""Component location field.

$Id: field.py,v 1.10 2003/07/04 10:59:16 ryzaja Exp $
"""
__metaclass__ = type

from zope.app import zapi
from zope.schema import Field
from zope.schema.interfaces import ValidationError
from zope.exceptions import NotFoundError
from zope.app.interfaces.services.field import IComponentPath
from zope.interface import implements

class ComponentPath(Field):

    implements(IComponentPath)

    _type = unicode

    def __init__(self, type, *args, **kw):
        self.type = type
        super(ComponentPath, self).__init__(*args, **kw)

    def _validate(self, value):
        super(ComponentPath, self)._validate(value)

        if not value.startswith('/'):
            raise ValidationError("Not an absolute path", value)

        try:
            component = zapi.traverse(self.context, value)
        except NotFoundError:
            raise ValidationError("Path for non-existent object", value)

        if not self.type.isImplementedBy(component):
            raise ValidationError("Wrong component type", value)

