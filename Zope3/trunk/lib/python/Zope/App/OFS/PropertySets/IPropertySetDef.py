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

$Id: IPropertySetDef.py,v 1.2 2002/06/10 23:28:08 jim Exp $"
"""
from Interface import Interface

class IPropertySetDef(Interface):

    """
    Interface to manage a collection of properties
    """

    def __init__():
        """
        Create an empty PropertySetDef
        """

    def addField(name,field):
        """
        Add a IField object to the PropertySet under name 'name'.
        """

    def getField(name):
        """
        Return the IField defining the property 'name'.
        """

    def has_field(name):
        """
        True if the PropertySet has a property named 'name'.
        """

    def fieldNames():
        """
        Returns a list of the property names defined by the PropertySet
        """

    def __iter__():
        """
        Returns an iterator over the IFields
        """

    def __len__():
        """
        Returns the number of fields in the PropertySetDef
        """
