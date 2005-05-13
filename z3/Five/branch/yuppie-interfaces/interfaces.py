##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
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
# be removed in Five 1.3. Please import interfaces from the corresponding Zope
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
    # BBB: for Zope 2.7 and 2.8.0
    from bbb.AccessControl_interfaces import *
    from bbb.Acquisition_interfaces import *
    from bbb.App_interfaces import *
    from bbb.OFS_interfaces import *
    from bbb.webdav_interfaces import *

    def monkey():
        import sys
        import bbb

        sys.modules['AccessControl.interfaces'] = bbb.AccessControl_interfaces
        sys.modules['Acquisition.interfaces'] = bbb.Acquisition_interfaces
        sys.modules['App.interfaces'] = bbb.App_interfaces
        sys.modules['OFS.interfaces'] = bbb.OFS_interfaces
        sys.modules['webdav.interfaces'] = bbb.webdav_interfaces
