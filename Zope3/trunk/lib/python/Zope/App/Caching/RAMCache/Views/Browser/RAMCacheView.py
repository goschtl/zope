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
"""RAMCache view

$Id: RAMCacheView.py,v 1.1 2002/10/31 16:01:40 alga Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.Caching.RAMCache.IRAMCache import IRAMCache

class RAMCacheView(BrowserView):

    __used_for__ = IRAMCache

    def action(self, request_vars=None, maxEntries=None, maxAge=None,
               cleanupInterval=None):
        self.context.update(request_vars, maxEntries, maxAge,
                            cleanupInterval)
        self.request.response.redirect('.')
