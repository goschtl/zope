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

import sys

from zope.interface import implements
import zope.component
from zope.publisher.interfaces.browser import IBrowserRequest
from z3c.form import util, button
from z3c.form.interfaces import IForm
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
BLUR = JSEvent("blur")
FOCUS = JSEvent("focus")
KEYDOWN = JSEvent("keydown")
KEYUP = JSEvent("keyup")
MOUSEDOWN = JSEvent("mousedown")
MOUSEMOVE = JSEvent("mousemove")
MOUSEOUT = JSEvent("mouseout")
MOUSEOVER = JSEvent("mouseover")
MOUSEUP = JSEvent("mouseup")
RESIZE = JSEvent("resize")
SELECT = JSEvent("select")
SUBMIT = JSEvent("submit")


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


class JSFormEventsRenderer(object):
    """IJSEventsRenderer implementation"""
    implements(interfaces.IJSFormEventsRenderer)
    zope.component.adapts(IForm)

    def __init__(self, form):
        self.form = form
        self.request = form.request

    def render(self):
        result = ''
        for widget in filter(interfaces.IJSEventsWidget.providedBy,
                             self.form.widgets.values()):
            renderer = zope.component.getMultiAdapter((widget.jsEvents, self.request),
                                                     interfaces.IJSEventsRenderer)
            result += renderer.render(widget, self.form)
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


class Handlers(button.Handlers):
    """Event Handlers for Javascript Buttons."""

    def addHandler(self, button, handler):
        """See z3c.form.interfaces.IButtonHandlers"""
        # Create a specification for the button
        buttonSpec = util.getSpecification(button)
        if isinstance(buttonSpec, util.classTypes):
            buttonSpec = zope.interface.implementedBy(buttonSpec)
        # Register the handler
        self._registry.register(
            (buttonSpec,), interfaces.IJSEventHandler, '', handler)
        self._handlers += ((button, handler),)

    def getHandler(self, button):
        """See z3c.form.interfaces.IButtonHandlers"""
        buttonProvided = zope.interface.providedBy(button)
        return self._registry.lookup1(buttonProvided, interfaces.IJSEventHandler)


class Handler(object):
    zope.interface.implements(interfaces.IJSEventHandler)

    def __init__(self, button, func, event=CLICK):
        self.button = button
        self.func = func
        self.event = event

    def __call__(self, form, id):
        return self.func(form, id)

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.button)


def handler(button, **kwargs):
    """A decorator for defining a javascript event handler."""
    def createHandler(func):
        handler = Handler(button, func, event=kwargs.get('event', CLICK))
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        jshandlers = f_locals.setdefault('jshandlers', Handlers())
        jshandlers.addHandler(button, handler)
        return handler
    return createHandler
