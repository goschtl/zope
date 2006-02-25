##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Five interfaces

$Id$
"""
from zope.interface import Interface
from zope.interface.interfaces import IInterface

class IBrowserDefault(Interface):
    """Provide a hook for deciding about the default view for an object"""

    def defaultView(self, request):
        """Return the object to be published
        (usually self) and a sequence of names to traverse to
        find the method to be published.
        """

class IMenuItemType(IInterface):
    """Menu item type

    Menu item types are interfaces that define classes of
    menu items.
    """


#
# BBB: Zope core interfaces
#
# The interfaces here are only provided for backwards compatibility and will
# be removed in Five 1.2. Please import interfaces from the corresponding Zope
# package instead.
#

try:
    from persistent.interfaces import IPersistent
except ImportError:
    # BBB: for Zope 2.7
    class IPersistent(Interface):
        """Persistent object"""

try:
    from AccessControl.interfaces import *
    from Acquisition.interfaces import *
    from App.interfaces import *
    from OFS.interfaces import *
    from webdav.interfaces import *

    def monkey():
        pass

except ImportError:
    # BBB: for Zope 2.7 and 2.8
    from Products.Five.bbb.AccessControl_interfaces import *
    from Products.Five.bbb.Acquisition_interfaces import *
    from Products.Five.bbb.App_interfaces import *
    from Products.Five.bbb.OFS_interfaces import *
    from Products.Five.bbb.webdav_interfaces import *

    def monkey():
        import sys
        from Products.Five.bbb import AccessControl_interfaces
        from Products.Five.bbb import Acquisition_interfaces
        from Products.Five.bbb import App_interfaces
        from Products.Five.bbb import OFS_interfaces
        from Products.Five.bbb import webdav_interfaces
        from Products.Five.bbb import z3bridge

        sys.modules['AccessControl.interfaces'] = AccessControl_interfaces
        sys.modules['Acquisition.interfaces'] = Acquisition_interfaces
        sys.modules['App.interfaces'] = App_interfaces
        sys.modules['OFS.interfaces'] = OFS_interfaces
        sys.modules['webdav.interfaces'] = webdav_interfaces
        sys.modules['Interface.bridge'] = z3bridge

# BBB: for old names used in Five 1.0
IAcquisition = IAcquirer
IPermissionMapping = IPermissionMappingSupport
