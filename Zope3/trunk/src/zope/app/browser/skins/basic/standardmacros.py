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
"""Standard macros for page templates in the ZMI

The macros are drawn from various different page templates.

$Id: standardmacros.py,v 1.3 2002/12/26 20:20:47 jim Exp $
"""
from zope.interface import Interface
from zope.interface.common.mapping import IItemMapping
from zope.component import getView
from zope.publisher.browser import BrowserView

class Macros:

    __implements__ = IItemMapping

    macro_pages = ()

    def __getitem__(self, key):
        context = self.context
        request = self.request
        for name in self.macro_pages:
            page = getView(context, name, request)
            try:
                v = page[key]
            except KeyError:
                pass
            else:
                return v
        raise KeyError, key


class StandardMacros(BrowserView, Macros):

    __implements__ = BrowserView.__implements__, Macros.__implements__

    macro_pages = ('view_macros', 'dialog_macros')
