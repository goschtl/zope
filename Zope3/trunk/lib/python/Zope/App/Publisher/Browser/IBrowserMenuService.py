##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: IBrowserMenuService.py,v 1.2 2002/10/01 12:49:08 jim Exp $
"""

from Interface import Interface

class IBrowserMenuService(Interface):

    def getMenu(menu_id, object, request):
        """Get a browser menu for an object and request

        Return a sequence of mapping objects with keys:

        title -- The menu item title

        description -- The item title

        action -- A (possibly relative to object) URL for the menu item.

        The entries returned are accessable to the current user and
        have passed any menu item filters, if any.

        """

    def getFirstMenuItem(menu_id, object, request):
        """Get the first browser menu item for an object and request

        Return a mapping object with keys:

        title -- The menu item title

        description -- The item title

        action -- A (possibly relative to object) URL for the menu item.

        The entry returned is accessable to the current user and
        has passed any menu item filters, if any.

        If no entry can be found, None is returned.
        """

        
