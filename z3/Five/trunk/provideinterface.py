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
from zope.component import getService, servicenames
from zope.interface import directlyProvides
from zope.interface.interfaces import IInterface
from types import ClassType

def provideInterface(id, interface, iface_type=None):
    """register Interface with utility service
    """
    if not id:
        id = "%s.%s" % (interface.__module__, interface.__name__)

    if not IInterface.providedBy(interface):
        if not isinstance(interface, (type, ClassType)):
            raise TypeError(id, "is not an interface or class")
        return

    if iface_type is not None:
        if not iface_type.extends(IInterface):
            raise TypeError(iface_type, "is not an interface type")
        directlyProvides(interface, iface_type)
    else:
        iface_type = IInterface

    utilityService = getService(servicenames.Utilities)
    utilityService.provideUtility(iface_type, interface, name=id)
