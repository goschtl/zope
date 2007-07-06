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
import zope.component
from zope.interface import implements
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.traversing.interfaces import IPathAdapter, ITraversable
from z3c.form import util, button
from z3c.form.interfaces import IForm
from jquery.layer import IJQueryJavaScriptBrowserLayer

from z3c.formjs import interfaces


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
            event = zope.component.getUtility(
                interfaces.IJSEvent, name=eventName)
            renderer = zope.component.getMultiAdapter(
                (event, self.request), interfaces.IJSEventRenderer)
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
        #first render events attached to widgets
        for widget in filter(interfaces.IJSEventsWidget.providedBy,
                             self.form.widgets.values()):
            renderer = zope.component.getMultiAdapter(
                (widget.jsEvents, self.request), interfaces.IJSEventsRenderer)
            result += renderer.render(widget, self.form)
        # render events attached to fields
        if hasattr(self.form, 'jshandlers'):
            for field in self.form.fields.values():
                handler = self.form.jshandlers.getHandler(field)
                if handler is not None:
                    renderer = zope.component.getMultiAdapter(
                        (handler.event, self.request),
                        interfaces.IJSEventRenderer)
                    # XXX: is this a safe way to get ids?
                    # Answer: Yes it is, because field is a z3c.form Field!
                    id = self.form.widgets[field.__name__].id
                    result += renderer.render(handler, id, self.form) + '\n'
            #render events attached to buttons
            if hasattr(self.form, 'buttons'):
                for key, button in self.form.buttons.items():
                    handler = self.form.jshandlers.getHandler(button)
                    if handler is not None:
                        renderer = zope.component.getMultiAdapter(
                            (handler.event, self.request),
                            interfaces.IJSEventRenderer)
                        # XXX: is this a safe way to get ids?
                        id = self.form.actions[key].id
                        result += renderer.render(handler, id, self.form) + '\n'

        return result


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
        return self._registry.lookup1(
            buttonProvided, interfaces.IJSEventHandler)


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


class JSEventPath(object):

    zope.component.adapts(None)
    zope.interface.implements(IPathAdapter, ITraversable)

    def __init__(self, context):
        self.context = context

    def traverse(self, name, furtherPath=[]):
        if name == 'renderer':
            return interfaces.IJSFormEventsRenderer(self.context)
