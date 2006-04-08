##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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
$Id$
"""

from zope.interface import directlyProvidedBy
from zope.interface import directlyProvides



def assertListOfInterfaces(value):
    """Assert a list of interfaces.

    This helper function asserts that a list of interfaces is returned:

        >>> from zope.interface import Interface

        >>> class IA(Interface):
        ...     pass

        >>> class IB(Interface):
        ...     pass

        >>> class IC(Interface):
        ...     pass

    An interface is returned as a list of this single interface:

        >>> result = assertListOfInterfaces(IA)
        >>> [iface.__name__ for iface in result]
        ['IA']

    A tuple of interface/interfaces is returned as list of interface/
    interfaces:

        >>> result = assertListOfInterfaces((IA, IB, IC))
        >>> [iface.__name__ for iface in result]
        ['IA', 'IB', 'IC']

    A list of interface/interfaces is returned as new list of interface/
    interfaces:

        >>> input = [IA, IB, IC]
        >>> result = assertListOfInterfaces(input)

        >>> input is result, input == result
        (False, True)

        >>> [iface.__name__ for iface in result]
        ['IA', 'IB', 'IC']

    None is returned as an empty list:

        >>> assertListOfInterfaces(None)
        []

    """

    if isinstance(value, (tuple, list)):
        # list/tuple of interfaces
        return list(value)
    elif value is None:
        # None
        return []
    else:
        # interface
        return [value]



def updateDirectlyProvided(self, value, previous_value=None):
    """Update directly provides after a value is set."""

    directlyProvided = list(directlyProvidedBy(self))
    for iface in assertListOfInterfaces(previous_value):
        if iface in directlyProvided:
            directlyProvided.remove(iface)

    directlyProvided = assertListOfInterfaces(value) + directlyProvided
    directlyProvides(self, *directlyProvided)
