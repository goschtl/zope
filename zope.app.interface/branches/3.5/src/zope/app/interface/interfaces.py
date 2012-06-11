##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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
"""Interfaces related to the local interface service.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface

class IInterfaceBasedRegistry(Interface):
    """Registries that use interfaces."""

    def getRegistrationsForInterface(iface):
        """Return registrations related to iface.

        The Return value is iterable of `IRegistration` object.
        """
