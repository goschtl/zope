##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""

$Id: StringBaseValidator.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

from Zope.App.Formulator.Validator import Validator
from types import StringType

  
class StringBaseValidator(Validator):
    """Simple string validator.
    """

    __implements__ = Validator.__implements__
    
    propertyNames = Validator.propertyNames + ['required']
    messageNames = Validator.messageNames + ['requiredNotFound']
    
    requiredNotFound = 'Input is required but no input given.'
    illegalValue = 'The value is not a string.'

        
    def validate(self, field, value):
        """ """
        if not isinstance(value, StringType):
            self.raiseError('illegalValue', field)
        value = value.strip()
        if field.getValue('isRequired') and value == "":
            self.raiseError('requiredNotFound', field)

        return value
