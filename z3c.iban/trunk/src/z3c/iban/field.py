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

class IBAN(zope.schema.TextLine):
    zope.interface.implements(interfaces.IIBAN)

    def _validate(self, value):
        if not valid(value):
            raise interfaces.NotValidIBAN(value)
        super(IBAN, self)._validate(value)
        
class BIC(zope.schema.TextLine):
    zope.interface.implements(interfaces.IBIC)
    
    def _validate(self, value):
        value = value.strip()
        if len(value) != 8 and len(value) != 11:
            # length must be 8 or 11 characters
            raise interfaces.NotValidBIC(value)
        if not value[:6].isalpha():
            # Characters 0-6 must be letters
            raise interfaces.NotValidBIC(value)
        if not value[6:8].isalnum():
            # Characters 7,8 must me alphanumeric
            raise interfaces.NotValidBIC(value)
        super(BIC, self)._validate(value)
        

