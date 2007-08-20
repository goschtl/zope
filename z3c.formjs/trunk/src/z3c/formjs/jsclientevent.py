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
"""Javascript Functions.

$Id: jsfunction.py 78862 2007-08-16 00:16:19Z srichter $
"""
__docformat__ = "reStructuredText"
import sys
import zope.component
import zope.interface
from zope.interface import adapter

from zope.security.management import getInteraction
from zope.publisher.interfaces.browser import IBrowserRequest

from z3c.formjs import interfaces, jsfunction

CLIENT_EVENT_REQUEST_KEY = "z3c.formjs.jsclientevent.caughtEvents"


class ClientEventHandlers(object):
    """Client Handlers for server side events."""

    def __init__(self):
        self._registry = adapter.AdapterRegistry()
        self._handlers = ()

    def addHandler(self, required, handler):
        """See interfaces.IClientEventHandlers"""
        # Register the handler
        self._registry.subscribe(
            required, interfaces.IClientEventHandler, handler)
        self._handlers += ((required, handler),)

    def getHandlers(self, event):
        """See interfaces.IClientEventHandlers"""
        return self._registry.subscribers((event.object, event), interfaces.IClientEventHandler)

    def copy(self):
        """See interfaces.IClientEventHandlers"""
        handlers = Handlers()
        for eventSpec, handler in self._handlers:
            handlers.addHandler(eventSpec, handler)
        return handlers

    def __add__(self, other):
        """See interfaces.IClientEventHandlers"""
        if not isinstance(other, ClientEventHandlers):
            raise NotImplementedError
        handlers = self.copy()
        for required, handler in other._handlers:
            handlers.addHandler(required, handler)
        return handlers

    def __repr__(self):
        return '<ClientEventHandlers %r>' %[handler for required, handler in self._handlers]


class ClientEventHandler(object):
    zope.interface.implements(interfaces.IClientEventHandler)

    def __init__(self, required, func):
        self.required = required
        self.func = func

    def __call__(self, form, event):
        return self.func(form, event)

    def __repr__(self):
        return '<%s for %r>' % (self.__class__.__name__, self.required)


def listener(required):
    """A decorator for defining a javascript function that is a listener."""
    def createListener(func):
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        handlers = f_locals.setdefault('jsClientListeners', ClientEventHandlers())
        jsListener = ClientEventHandler(required, func)
        return handlers.addHandler(required, jsListener)
    return createListener

def serverToClientEventLoader(event):
    """Event handler that listens for server side events
    and stores the event in the request to be picked up by
    the form and rendered as a client side function call."""

    #step 1: get the interaction
    interaction = getInteraction()
    participations = interaction.participations

    #step 2: look for a request in the participation
    request = None
    for part in participations:
        if IBrowserRequest.providedBy(part):
            request = part
            break
    #if no request was found, we have nothing to do.
    if request is None:
        return
    #step 3: add the event to the list of events this handler has caught.
    events = request.annotations.setdefault(CLIENT_EVENT_REQUEST_KEY, [])
    if event not in events:
        events.append(event)


class ClientEventsForm(object):
    """Mixin class to support calling of client side events."""

    jsClientListeners = ClientEventHandlers()

    @property
    def eventCalls(self):
        events = self.request.annotations.get(CLIENT_EVENT_REQUEST_KEY, [])
        result = []
        for event in events:
            if self.jsClientListeners.getHandlers(event):
                result.append(event)
        return result

    @property
    def eventInjections(self):
        results = []
        for event in self.eventCalls:
            results += self.jsClientListeners.getHandlers(event)
        results = '\n'.join(results)
        return results
