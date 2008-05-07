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
import zope.interface
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.viewlet import viewlet

from z3c.formjs import interfaces


class JSEvent(object):
    """Javascript Event"""
    zope.interface.implements(interfaces.IJSEvent)

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

EVENTS = (CLICK, DBLCLICK, CHANGE, LOAD, BLUR, FOCUS, KEYDOWN, KEYUP,
          MOUSEDOWN, MOUSEMOVE, MOUSEOUT, MOUSEOVER, MOUSEUP, RESIZE, SELECT,
          SUBMIT)

class IdSelector(object):
    zope.interface.implements(interfaces.IIdSelector)

    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '<%s "%s">' %(self.__class__.__name__, self.id)


class CSSSelector(object):
    zope.interface.implements(interfaces.ICSSSelector)

    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return '<%s "%s">' %(self.__class__.__name__, self.expr)


class JSSubscription(object):
    zope.interface.implements(interfaces.IJSSubscription)

    def __init__(self, event, selector, handler):
        self.event = event
        self.selector = selector
        self.handler = handler

    def __repr__(self):
        return '<%s event=%r, selector=%r, handler=%r>' % (
            self.__class__.__name__, self.event, self.selector, self.handler)


class JSSubscriptions(object):
    zope.interface.implements(interfaces.IJSSubscriptions)

    def __init__(self):
        self._subscriptions = {}

    def subscribe(self, event, selector, handler):
        subscription = JSSubscription(event, selector, handler)
        name = handler.__name__
        subscriptions = self._subscriptions.get(name, [])
        subscriptions.append(subscription)
        self._subscriptions[name] = subscriptions
        return subscription

    def __iter__(self):
        for subscriptions in self._subscriptions.values():
            for subscription in subscriptions:
                yield subscription

    def __getitem__(self, name):
        return self._subscriptions[name]


def subscribe(selector, event=CLICK):
    """A decorator for defining a javascript event handler."""
    def createSubscription(func):
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        subs = f_locals.setdefault('jsSubscriptions', JSSubscriptions())
        subs.subscribe(event, selector, func)
        func.__dict__['selector'] = selector
        func.__dict__['event'] = event
        return func
    return createSubscription


class JSSubscriptionsViewlet(viewlet.ViewletBase):
    """An viewlet for the JS viewlet manager rendering subscriptions."""
    zope.component.adapts(
        zope.interface.Interface,
        IBrowserRequest,
        interfaces.IHaveJSSubscriptions,
        zope.interface.Interface)

    # This viewlet wants to be very heavy, so that it is rendered after all
    # the JS libraries are loaded.
    weight = 1000

    def update(self):
        self.renderer = zope.component.getMultiAdapter(
            (self.__parent__.jsSubscriptions, self.request),
            interfaces.IRenderer)
        self.renderer.update()

    def render(self):
        content = self.renderer.render()
        return u'<script type="text/javascript">\n%s\n</script>' % content
