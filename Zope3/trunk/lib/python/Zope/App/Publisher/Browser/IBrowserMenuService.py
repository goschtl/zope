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
$Id: IBrowserMenuService.py,v 1.1 2002/06/18 19:34:57 jim Exp $
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

        
