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
$Id: IValidator.py,v 1.1 2002/09/05 18:55:03 jim Exp $
"""
from Interface import Interface

class IValidator(Interface):
    """Validates a particular value against the specifed field. Each
    Validator just does one check, like check for the max value or the
    min value!

    Note that the responsibility of Validator is not to change the
    value, only to raise an exception in case the value was incorrect.
    Converters are used to change values.
    
    It should be always implemented as an adapter.
    """

    def validate(value):
        """Validate the the value.

        This should not return anything, only raise an exception in case
        of an invalid value.""" 
