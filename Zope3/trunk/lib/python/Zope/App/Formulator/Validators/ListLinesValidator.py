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

$Id: ListLinesValidator.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

from LinesValidator import LinesValidator

class ListLinesValidator(LinesValidator):
    """A validator that can deal with lines that have a | separator
    in them to split between text and value of list items.
    """

    __implements__ = LinesValidator.__implements__
    
    def validate(self, value):
        
        value = Validator.LinesValidator.validate(value)
        result = []
        for line in value:
            elements = string.split(line, "|")
            if len(elements) >= 2:
                text, value = elements[:2]
            else:
                text = line
                value = line
            text = string.strip(text)
            value = string.strip(value)
            result.append((text, value))
        return result
