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

$Id: StringValidator.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

from StringBaseValidator import StringBaseValidator


class StringValidator(StringBaseValidator):
    """ """

    __implements__ = StringBaseValidator.__implements__
    

    propertyNames = StringBaseValidator.propertyNames + \
                    ['maxLength', 'truncate']
    maxLength = 0
    truncate = 0
    
    messageNames = StringBaseValidator.messageNames + \
                    ['tooLong']

    tooLong = 'Too much input was given.'


    def validate(self, field, value):
        value = StringBaseValidator.validate(self, field, value)

        maxLength = self.maxLength or 0
        
        if maxLength > 0 and len(value) > maxLength:
            if self.truncate:
                value = value[:maxLength]
            else:
                self.raiseError('tooLong', field)

        return value

