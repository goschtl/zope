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

$Id: field.py,v 1.3 2003/01/09 17:28:44 stevea Exp $
"""
__metaclass__ = type

from zope.schema.interfaces import IField
from zope.schema import Field
from zope.schema.interfaces import ValidationError
from zope.app.traversing import traverse
from zope.app.component.interfacefield import InterfaceField
from zope.exceptions import NotFoundError

class IComponentPath(IField):
    """A field containing a component path.
    """

    type = InterfaceField(
        title = u"An interface that must be implemented by the component.",
        required = True,
        readonly = True,
        basetype = None
        )

class ComponentPath(Field):

    __implements__ = IComponentPath

    _type = unicode

    def __init__(self, type, *args, **kw):
        self.type = type
        super(ComponentPath, self).__init__(*args, **kw)

    def _validate(self, value):
        super(ComponentPath, self)._validate(value)

        if not value.startswith('/'):
            raise ValidationError("Not an absolute path", value)

        try:
            component = traverse(self.context, value)
        except NotFoundError:
            raise ValidationError("Path for non-existent object", value)

        if not self.type.isImplementedBy(component):
            raise ValidationError("Wrong component type", value)


