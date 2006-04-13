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

__docformat__ = 'restructuredtext'

from zope.dottedname.resolve import resolve
from zope.interface.interfaces import IInterface

from zope.generic.component import IKeyInterface



def toDottedName(component):
    if component is None:
        return 'None'
    return component.__module__ + '.' + component.__name__


# cache
__name_to_component = {}

def toComponent(name):
    try:
        return __name_to_component[name]
    except KeyError:
        return __name_to_component.setdefault(name, resolve(name))



def getKey(component):
    """Evaluate the interface key from a component."""

    if IInterface.providedBy(component):
        interface = component

    elif IKeyInterface.providedBy(component):
        interface = component.interface

    else:
        interface = IKeyInterface(component).interface

    return interface



def queryKey(component, default=None):
    """Evaluate the interface key from a component."""

    try:
        return getKey(component)

    except:
        return default
