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

$Id: EmailValidator.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

import re
from StringValidator import StringValidator

class EmailValidator(StringValidator):

    __implements__ = StringValidator.__implements__

    messageNames = StringValidator.messageNames + ['notEmail']

    notEmail = 'You did not enter an email address.'

    # contributed, I don't pretend to understand this..
    pattern = re.compile("^([0-9a-z_&.+-]+!)*[0-9a-z_&.+-]+"
                         "@(([0-9a-z]([0-9a-z-]*[0-9a-z])?\.)+"
                         "[a-z]{2,3}|([0-9]{1,3}\.){3}[0-9]{1,3})$")
    
    def validate(self, field, value):
        value = StringValidator.validate(self, field, value)

        if value == "" and not field.getValue('isRequired'):
            return value

        if self.pattern.search(value.lower()) == None:
            self.raiseError('notEmail', field)
        return value
