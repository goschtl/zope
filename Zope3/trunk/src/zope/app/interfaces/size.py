
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
"""Interfaces that give the size of an object.

$Id: size.py,v 1.1 2002/12/27 15:22:52 stevea Exp $
"""

from zope.interface import Interface, Attribute

# basic units:
#   'bytes'
#   'number'  (for example, number of subobjects for a folder)
#   None  (for unsized things)
#
# We can use the sizeForSorting to get us sizes all in bytes for example.

class ISized(Interface):

    def sizeForSorting():
        """Returns a tuple (basic_unit, amount)
        
        Used for sorting among different kinds of sized objects.
        'amount' need only be sortable among things that share the
        same basic unit."""
        
    def sizeForDisplay():
        """Returns a string giving the size.
        """

