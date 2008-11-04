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
"""IBAN Field implementation

$Id: field.py 78339 2007-07-25 22:55:36Z hermann $
"""

__docformat__ = "reStructuredText"

from ibanlib.iban import valid

import zope.interface
import zope.schema
from zope.schema.fieldproperty import FieldProperty

from z3c.iban import interfaces

class IBAN(zope.schema.Orderable, zope.schema.Field):
    zope.interface.implements(interfaces.IIBAN)

    def _validate(self, value):
        if not valid(value):
            raise zope.schema.ValidationError(
                "Value is no valid IBAN")
        super(IBAN, self)._validate(value)

