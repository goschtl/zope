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

$Id: InterfaceField.py,v 1.2 2002/12/04 09:54:04 jim Exp $
"""

from Zope.Schema.IField import IEnumeratable
from Zope.Schema import Enumeratable
from Interface import Interface
from Interface.IInterface import IInterface
from Zope.Schema.Exceptions import ValidationError

class IInterfaceField(IEnumeratable):
    u"""Fields with Interfaces as values
    """
    
class InterfaceField(Enumeratable):
    __doc__ = IInterfaceField.__doc__
    __implements__ = IInterfaceField


    def _validate(self, value):
        super(InterfaceField, self)._validate(value)

        if not IInterface.isImplementedBy(value):
            raise ValidationError("Not an interface", value)


