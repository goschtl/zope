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

$Id: TextValidator.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

from LinesValidator import LinesValidator

class TextValidator(LinesValidator):
    """ """
    
    def validate(self, field, value):
        value = LinesValidator.validate(self, field, value)
        # we need to add this check again
        if value == [] and not field.get_value('isRequired'):
            return ""

        # join everything into string again with \n and return
        return "\n".join(value)

