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
$Id: IConverter.py,v 1.2 2002/09/07 16:18:48 jim Exp $
"""
from Interface import Interface

class IConverter(Interface):
    """A converter can convert a value from one type to another."""

    def convert(value):
        """Call an IConverter with a value, and it will try to convert to
        another value and return the result. If conversion cannot take
        place, the convertor will raise a ConversionError.
        """
    
