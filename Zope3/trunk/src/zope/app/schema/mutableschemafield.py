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
"""Defines fields that are used in mutable schemas.

$Id: mutableschemafield.py,v 1.1 2004/03/10 00:57:56 srichter Exp $
"""
from zope.interface import implements, providedBy
from zope.interface.interfaces import IInterface
from zope.schema.interfaces import ValidationError
from zope.app.component.interfacefield import InterfaceField, InterfacesField

from interfaces import IMutableSchemaField, IMutableSchemasField, IMutableSchema

class MutableSchemaField(InterfaceField):

    __doc__ = IMutableSchemaField.__doc__
    implements(IMutableSchemaField)
    basetype = None

    def __init__(self, basetype=IMutableSchema, *args, **kw):
        # XXX Workaround for None indicating a missing value
        if basetype is None:
            kw['required'] = False
        super(MutableSchemaField, self).__init__(basetype=basetype,
                                                 *args, **kw)

    def _validate(self, value):
        basetype = self.basetype

        if value is None and basetype is None:
            return

        if basetype is None:
            basetype = IMutableSchema

        if not IInterface.providedBy(value):
            raise ValidationError("Not an interface", value)

        if basetype in providedBy(value):
            return

        if not value.extends(basetype, 0):
            raise ValidationError("Does not extend", value, basetype)


class MutableSchemasField(InterfacesField):

    __doc__ = IMutableSchemasField.__doc__
    implements(IMutableSchemasField)
    basetype = None

    def __init__(self, basetype=IMutableSchema, default=(), *args, **kw):
        # XXX Workaround for None indicating a missing value
        if basetype is None:
            kw['required'] = False
        super(MutableSchemasField, self).__init__(basetype=basetype,
                                                  default=default, *args, **kw)

    def _validate(self, value):
        basetype = self.basetype

        if value is () and basetype is None:
            return

        if basetype is None:
            basetype = IMutableSchema

        for v in value:
            if not IInterface.providedBy(v):
                raise ValidationError("Not an interface", v)

        for v in value:
            if basetype in providedBy(v):
                return

        for v in value:
            if not v.extends(basetype, 0):
                raise ValidationError("Does not extend", v, basetype)
