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

$Id: BooleanValidator.py,v 1.2 2002/06/10 23:27:48 jim Exp $
"""

from Zope.App.Formulator.Validator import Validator

class BooleanValidator(Validator):

    __implements__ = Validator.__implements__

    
    def validate(self, field, value):

        if value in ['t', 1]:
            return 1

        if value in ['f', 0, '', None]:
            return 0

        # XXX Should raise some sort of error
