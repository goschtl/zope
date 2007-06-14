##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Javascript Form Framework Event Framework.

$Id: $
"""
__docformat__ = "reStructuredText"

from zope.interface import implements
from zope.component import adapts

from jquery.layer import IJQueryJavaScriptBrowserLayer

import interfaces

class JSEvent(object):
    """IJSEvent implementation.

    See ``interfaces.IJSEvent``.
    """
    implements(interfaces.IJSEvent)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<JSEvent "%s">' % self.name

CLICK = JSEvent("click")
DBLCLICK = JSEvent("dblclick")
CHANGED = JSEvent("changed")
LOAD = JSEvent("load")


class JQueryEventRenderer(object):
    """IJSEventRenderer implementation.

    See ``interfaces.IJSEventRenderer``.
    """
    implements(interfaces.IJSEventRenderer)
    adapts(interfaces.IJSEvent,
           IJQueryJavaScriptBrowserLayer)

    def __init__(self, event, request):
        self.request = request
        self.event = event

    def render(self, handler, id, form):
        return '$("#%s").bind("%s", function(){%s});' % (id, self.event.name, handler(form, id))
