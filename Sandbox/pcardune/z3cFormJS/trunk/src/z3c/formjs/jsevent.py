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
import zope.component
from zope.publisher.interfaces.browser import IBrowserRequest
from z3c.form import util
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
CHANGE = JSEvent("change")
LOAD = JSEvent("load")


class JSEvents(util.SelectionManager):
    """Selection manager for IJSEvents."""

    implements(interfaces.IJSEvents)

    def __init__(self, *args, **kwargs):
        super(JSEvents, self).__init__(*args, **kwargs)
        for kw in kwargs:
            self._data_keys.append(kw)
            self._data_values.append(kwargs[kw])
            self._data[kw] = kwargs[kw]


class JSEventsRenderer(object):
    """IJSEventsRenderer implementation"""
    implements(interfaces.IJSEventsRenderer)
    zope.component.adapts(interfaces.IJSEvents,
                          IBrowserRequest)

    def __init__(self, events, request):
        self.request = request
        self.events = events

    def render(self, widget, form):
        result = ''
        for eventName, handler in self.events.items():
            event = zope.component.getUtility(interfaces.IJSEvent, name=eventName)
            renderer = zope.component.queryMultiAdapter((event, self.request),
                                                        interfaces.IJSEventRenderer,
                                                        default=JQueryEventRenderer(event, self.request))
            result += renderer.render(handler, widget.id, form) + '\n'
        return result


class JQueryEventRenderer(object):
    """IJSEventRenderer implementation.

    See ``interfaces.IJSEventRenderer``.
    """
    implements(interfaces.IJSEventRenderer)
    zope.component.adapts(interfaces.IJSEvent,
                          IJQueryJavaScriptBrowserLayer)

    def __init__(self, event, request):
        self.request = request
        self.event = event

    def render(self, handler, id, form):
        return '$("#%s").bind("%s", function(){%s});' % (id, self.event.name, handler(form, id))
