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
$Id: menu.py,v 1.3 2003/06/06 21:35:15 philikon Exp $
"""

from zope.interface import implements
from zope.publisher.browser import BrowserView
from zope.app.interfaces.browser.menu import IMenuAccessView
from zope.component import getService

class MenuAccessView(BrowserView):
    __doc__ = IMenuAccessView.__doc__

    implements(IMenuAccessView)

    def __getitem__(self, menu_id):
        context = self.context
        request = self.request
        browser_menu_service = getService(context, 'BrowserMenu')
        return browser_menu_service.getMenu(menu_id,
                                            self.context,
                                            self.request)


__doc__ = MenuAccessView.__doc__ + __doc__
