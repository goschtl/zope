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

$Id: PatternValidator.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

from StringValidator import StringValidator
import PatternChecker

class PatternValidator(StringValidator):

    __implements__ = StringValidator.__implements__

    # does the real work
    checker = PatternChecker.PatternChecker()
    
    propertyNames = StringValidator.propertyNames +\
                     ['pattern']

    pattern = ""

    messageNames = StringValidator.messageNames +\
                    ['patternNotMatched']

    patternNotMatched = "The entered value did not match the pattern."

    def validate(self, field, value):
        value = StringValidator.validate(self, field, value)
        
        if value == "" and not field.get_value('required'):
            return value

        value = self.checker.validate_value([field.get_value('pattern')],
                                            value)
        if value is None:
            self.raise_error('patternNotMatched', field)
        return value
