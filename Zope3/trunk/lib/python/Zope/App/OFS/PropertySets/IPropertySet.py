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

$Id: IPropertySet.py,v 1.2 2002/06/10 23:28:08 jim Exp $"
"""
from Interface import Interface

class IPropertySet(Interface):

    """
    Interface to access a collection of properties
    """

    def __getitem__(name):
        """
        Return the value associated with the property
        """

    def __setitem__(name, value):
        """
        Store the value for the property.
        """

    def getField(name):
        """
        Get the IField that defines the property 'name'.
        """

    def has_field(name):
        """
        True if the PropertySet has the property name
        """

    def fieldNames():
        """
        Returns a list of the names of the properties
        """

    def __iter__():
        """
        Returns an iterator over the names of the properties
        """

    def __len__():
        """
        Returns the number of properties in the PropertySet
        """
