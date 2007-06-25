##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Currency Field implementation

$Id$
"""
__docformat__ = "reStructuredText"
import decimal
import zope.interface
import zope.schema
from zope.schema.fieldproperty import FieldProperty

from z3c.currency import interfaces

class Currency(zope.schema.Orderable, zope.schema.Field):
    zope.interface.implements(interfaces.ICurrency)

    precision = FieldProperty(interfaces.ICurrency['precision'])
    unit = FieldProperty(interfaces.ICurrency['unit'])

    def __init__(self, precision=interfaces.CENTS, unit=u'$', *args, **kw):
        super(Currency, self).__init__(*args, **kw)
        self.precision = precision
        self.unit = unit

    def validate(self, value):
        if not isinstance(value, decimal.Decimal):
            raise zope.schema.ValidationError(
                "Value must be of type 'Decimal', not '%s'." % (
                type(value).__name__) )

        if self.precision is interfaces.DOLLARS and value.as_tuple()[-1] != 0:
            raise zope.schema.ValidationError(
                "The value must be a whole number.")

        if self.precision is interfaces.CENTS and value.as_tuple()[-1] != -2:
            raise zope.schema.ValidationError(
                "The value must have two decimal places.")

        super(Currency, self).validate(value)
