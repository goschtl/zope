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
$Id: IConverter.py,v 1.1 2002/07/14 13:32:53 srichter Exp $
"""

from Interface import Interface
from Interface.Attribute import Attribute


class IConverter(Interface):
    """Converts from one type of Field type to another one. Most common will
    be to convert from String to another type, such as Integer."""

    __convert_to__ = Attribute('The field type this converter converts to.')
    __convert_from__ = Attribute('The field type this converter accepts '
                                 'for conversion.')

    def convert(value):
        """This method converts from __convert_from__ to __convert_to__."""
