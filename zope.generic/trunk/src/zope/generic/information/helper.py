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

from zope.component import getUtility
from zope.component import getUtilitiesFor
from zope.interface.interfaces import IInterface

from zope.generic.component import IKeyInterface
from zope.generic.component.api import toComponent
from zope.generic.component.api import toDottedName

from zope.generic.information import IInformationRegistryInformation



def getInformation(object, registry):
    """Evaluate an information from an object."""

    if IInterface.providedBy(object):
        interface = object

    elif IKeyInterface.providedBy(object):
        interface = object.interface

    else:
        interface = IKeyInterface(object).interface

    return getUtility(registry, toDottedName(interface))



def queryInformation(interface, registry, default=None):
    """Request an information or return default."""
    try:
        return getInformation(interface, registry)

    except:
        return default



def queryInformationRegistry(interface, default=None):
    return queryInformation(interface, IInformationRegistryInformation, default)



def registeredInformations(registry, default=None):
    for name, information in getUtilitiesFor(registry):
        yield (toComponent(name), information)
