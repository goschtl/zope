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
from zope.security.management import getInteraction
from zope.publisher.interfaces.browser import IBrowserRequest

from z3c.formjs import interfaces, jsfunction

def listener(eventType):
    """A decorator for defining a javascript function that is a listener."""
    namespace = "%s_%s" % (eventType.__module__.replace(".","_"), eventType.__name__)
##     def createFunction(func):
##         import pdb; pdb.set_trace()
##         frame = sys._getframe(1)
##         f_locals = frame.f_locals
##         funcs = f_locals.setdefault('jsFunctions', jsfunction.JSFunctions())
##         jsFunction = jsfunction.JSFunction(namespace, func)
##         return funcs.add(jsFunction, namespace)

    zope.component.provideHandler(serverToClientEventLoader, (eventType,))
    return jsfunction.function(namespace) #createFunction

CLIENT_EVENT_REQUEST_KEY = "z3c.formjs.jsclientevent.caughtEvents"

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

    @property
    def eventCalls(self):
        return self.request.annotations.get(CLIENT_EVENT_REQUEST_KEY, [])
