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

$Id: IntegerValidator.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

from StringBaseValidator import StringBaseValidator

class IntegerValidator(StringBaseValidator):
    """ """

    __implements__ = StringBaseValidator.__implements__

    propertyNames = StringBaseValidator.propertyNames +\
                    ['start', 'end']

    start = ""
    end = ""
    messageNames = StringBaseValidator.messageNames +\
                   ['notInteger', 'integerOutOfRange']

    notInteger = 'You did not enter an integer.'
    integerOutOfRange = 'The integer you entered was out of range.'

    def validate(self, field, value):
        value = StringBaseValidator.validate(self, field, value)
        
        # we need to add this check again
        if value == "" and not field.getValue('isRequired'):
            return value

        try:
            value = int(value)
        except ValueError:
            self.raiseError('notInteger', field)

        if self.start != "" and value < self.start:
            self.raiseError('integerOutOfRange', field)
        if self.end != "" and value >= self.end:
            self.raiseError('integerOutOfRange', field)
        return value
