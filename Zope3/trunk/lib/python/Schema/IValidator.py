##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: IValidator.py,v 1.1 2002/07/14 13:32:53 srichter Exp $
"""
from Interface import Interface

class IValidator(Interface):
    """It's repsonsibility lies in validating a particular value against the
    specifed field. Each Validator just does one check, like check for the
    max value or the min value!

    It should be always implemented as an adapter.
    """

    def validate(value):
        """Validate the the value. Note that this method must always
        return the value.""" 
