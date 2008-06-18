##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Interfaces for zope.introspector.
"""
from zope import interface, schema

class IIntrospectorBaseClasses(interface.Interface):
    ObjectInfo = interface.Attribute("Basic Object Information")
    UtilityInfo = interface.Attribute("Utilities an object can access")

class IIntrospectorAPI(IIntrospectorBaseClasses):
    """The API of zope.introspector.
    """
    pass

class IObjectInfo(interface.Interface):
    """Information about simple types.
    """
    def getType():
        """Get the type of the object handled here.
        """

class IUtilityInfo(interface.Interface):
    """Information about utilities available to an object.
    """
    def getAllUtilities():
        """Get all utilities available to an object.
        """
