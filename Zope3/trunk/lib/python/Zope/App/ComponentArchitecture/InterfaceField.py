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

$Id: InterfaceField.py,v 1.3 2002/12/05 13:27:02 dannu Exp $
"""

from Zope.Schema.IField import IValueSet
from Zope.Schema import ValueSet
from Interface import Interface
from Interface.IInterface import IInterface
from Zope.Schema.Exceptions import ValidationError

class IInterfaceField(IValueSet):
    u"""Fields with Interfaces as values
    """
    
class InterfaceField(ValueSet):
    __doc__ = IInterfaceField.__doc__
    __implements__ = IInterfaceField


    def _validate(self, value):
        super(InterfaceField, self)._validate(value)

        if not IInterface.isImplementedBy(value):
            raise ValidationError("Not an interface", value)


