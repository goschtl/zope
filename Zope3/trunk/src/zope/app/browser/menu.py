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
$Id: menu.py,v 1.2 2002/12/25 14:12:26 jim Exp $
"""

from zope.publisher.browser import BrowserView
from zope.app.interfaces.browser.menu import IMenuAccessView
from zope.component import getService

class MenuAccessView(BrowserView):
    __doc__ = IMenuAccessView.__doc__

    __implements__ = BrowserView.__implements__, IMenuAccessView

    def __getitem__(self, menu_id):
        context = self.context
        request = self.request
        browser_menu_service = getService(context, 'BrowserMenu')
        return browser_menu_service.getMenu(menu_id,
                                            self.context,
                                            self.request)


__doc__ = MenuAccessView.__doc__ + __doc__
