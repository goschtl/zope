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

$Id: LinesValidator.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

from StringBaseValidator import StringBaseValidator


class LinesValidator(StringBaseValidator):

    propertyNames = StringBaseValidator.propertyNames +\
                     ['maxLines', 'maxLineLength', 'maxLength']

    maxLines = ""
    maxLineLength = ""
    maxLength = ""
    
    messagenNames = StringBaseValidator.messageNames +\
                   ['tooManylines', 'lineTooLong', 'tooLong']

    tooManyLines = 'You entered too many lines.'
    lineTooLong = 'A line was too long.'
    tooLong = 'You entered too many characters.'

    
    def validate(self, field, value):
        value = StringBaseValidator.validate(self, field, value)
        # we need to add this check again
        if value == "" and not field.get_value('required'):
            return []
        
        # check whether the entire input is too long
        maxLength = field.get_value('maxLength') or 0
        if maxLength and len(value) > maxLength:
            self.raise_error('tooLong', field)
        # split input into separate lines
        lines = string.split(value, "\n")

        # check whether we have too many lines
        maxLines = field.get_value('maxLines') or 0
        if maxLines and len(lines) > maxLines:
            self.raise_error('tooManyLines', field)

        # strip extraneous data from lines and check whether each line is
        # short enough
        maxLineLength = field.get_value('maxLineLength') or 0
        result = []
        for line in lines:
            line = string.strip(line)
            if maxLineLength and len(line) > maxLineLength:
                self.raise_error('lineTooLong', field)
            result.append(line)
            
        return result
