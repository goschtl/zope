##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""
Utility Interface Definitions

$Id$
"""
from zope.interface import Interface


class IReadInterface(Interface):

    def getDirectlyProvided(obj):
        """List the interfaces directly implemented by an object.
        """

    def getDirectlyProvidedNames(obj):
        """List the names of interfaces directly implemented by an object.
        """

    def getAvailableInterfaces(obj):
        """List the marker interfaces available for this object.
        """

    def getAvailableInterfaceNames(obj):
        """List the names of marker interfaces available for this object.
        """

    def getProvided(obj):
        """List interfaces provided by an object.
        """

    def getDirectlyProvidedNames(obj):
        """List the names of interfaces provided by an object.
        """


class IWriteInterface(Interface):

    def update(obj, add=(), remove=()):
        """Update directly provided interfaces for an instance."""

    def mark(obj, interface):
        """ add interface to interfaces an object directly provides"""

    def erase(obj, interface):
        """ remove interfaces from interfaces an object directly provides"""


class IMarkerUtility(IReadInterface, IWriteInterface):
    """This utility provides methods for inspecting interfaces. And provides
       'mark' and 'erase' methods to add and remove marker interfaces
    """
