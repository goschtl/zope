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
"""WebDev Menu Implementation

$Id$
"""
__docformat__ = "reStructuredText"

import persistent
from zope.app.publisher.browser import menu

class BrowserMenu(menu.BrowserMenu, persistent.Persistent):
    """A persistent browser menu."""

    def __init__(self, id, title=u'', description=u'', menuItemType=None):
        self.id = id
        self.title = title
        self.description = description
        self.menuItemType = menuItemType

    def getMenuItemType(self):
        """See zope.app.publisher.interfaces.browser.IBrowserMenu"""
        return self.menuItemType
