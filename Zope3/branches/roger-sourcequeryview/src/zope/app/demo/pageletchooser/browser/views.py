##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""PageletChooser Demo

$Id:$
"""
__docformat__ = 'restructuredtext'

from zope.app.publisher.browser import BrowserView

from zope.app.demo.pageletchooser.interfaces import IPageletChooserContent



class PageletChooserContentView(BrowserView):
    """Provide an index view for PageletChooserContent."""

    __used_for__ = IPageletChooserContent

    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    def title(self):
        return self.context.title
        
    def description(self):
        return self.context.description
