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

$Id: FloatValidator.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

from StringBaseValidator import StringBaseValidator


class FloatValidator(StringBaseValidator):

    __implements__ = StringBaseValidator.__implements__

    messageNames = StringBaseValidator.messageNames + ['notFloat']
    notFloat = "You did not enter a floating point number."


    def validate(self, field, value):
        value = StringBaseValidator.validate(self, field, value)
        if value == "" and not field.getValue('isRequired'):
            return value

        try:
            value = float(value)
        except ValueError:
            self.raiseError('notFloat', field)
        return value
