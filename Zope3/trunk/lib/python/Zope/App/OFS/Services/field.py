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

$Id: field.py,v 1.2 2002/12/19 20:38:21 jim Exp $
"""
__metaclass__ = type

from Zope.Schema.IField import IField
from Zope.Schema import Field
from Zope.Schema.Exceptions import ValidationError
from Zope.App.Traversing import traverse
from Zope.App.ComponentArchitecture.InterfaceField import InterfaceField
from Zope.Exceptions import NotFoundError

class IComponentLocation(IField):
    """A field containing a component path.
    """

    type = InterfaceField(
        title = u"An interface that must be implemented by the component.",
        required = True,
        readonly = True,
        )

class ComponentLocation(Field):

    __implements__ = IComponentLocation

    _type = unicode

    def __init__(self, type, *args, **kw):
        self.type = type
        super(ComponentLocation, self).__init__(*args, **kw)

    def _validate(self, value):
        super(ComponentLocation, self)._validate(value)
        
        if not value.startswith('/'):
            raise ValidationError("Not an absolute path", value)
        
        try:
            component = traverse(self.context, value)
        except NotFoundError:
            raise ValidationError("Path for non-existent object", value)
        
        if not self.type.isImplementedBy(component):
            raise ValidationError("Wrong component type")
