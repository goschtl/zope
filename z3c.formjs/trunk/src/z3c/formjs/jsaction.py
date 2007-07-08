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
"""Javascript Form Framework Button Framework.

$Id: $
"""
__docformat__ = "reStructuredText"
import sys
import zope.component
import zope.interface
import zope.location
from zope.interface import adapter
from z3c.form import button, action, util
from z3c.form.browser.button import ButtonWidget
from z3c.form.interfaces import IField, IFieldWidget
from z3c.form.interfaces import IFormLayer, IFormAware
from z3c.form.interfaces import IButtonAction, IAfterWidgetUpdateEvent

from z3c.formjs import interfaces, jsevent


class WidgetSelector(jsevent.IdSelector):
    zope.interface.implements(interfaces.IWidgetSelector)

    def __init__(self, widget):
        self.widget = widget

    @property
    def id(self):
        return self.widget.id


class JSButton(button.Button):
    """A simple javascript button in a form."""
    zope.interface.implements(interfaces.IJSButton)


class JSButtonAction(action.Action, ButtonWidget, zope.location.Location):
    """A button action specifically for JS buttons."""
    zope.interface.implements(IButtonAction)
    zope.component.adapts(IFormLayer, interfaces.IJSButton)

    def __init__(self, request, field):
        action.Action.__init__(self, request, field.title)
        ButtonWidget.__init__(self, request)
        self.field = field

    @property
    def accesskey(self):
        return self.field.accessKey

    @property
    def value(self):
        return self.title

    @property
    def id(self):
        return self.name.replace('.', '-')


class JSHandlers(object):
    """Advanced Javascript event handlers for fields and buttons.

    This implementation of the Javascript event handlers interface used an
    adapter registry to manage more general versus more specific handler
    registrations. When asked for handlers, the registry will always return
    the most specific one for each event.
    """
    zope.interface.implements(interfaces.IJSEventHandlers)

    def __init__(self):
        self._registry = adapter.AdapterRegistry()
        self._handlers = ()

    def addHandler(self, field, event, handler):
        """See interfaces.IJSEventHandlers"""
        # Create a specification for the field and event
        fieldSpec = util.getSpecification(field)
        eventSpec = util.getSpecification(event)
        if isinstance(fieldSpec, util.classTypes):
            fieldSpec = zope.interface.implementedBy(fieldSpec)
        if isinstance(eventSpec, util.classTypes):
            eventSpec = zope.interface.implementedBy(eventSpec)
        # Register the handler
        self._registry.register(
            (fieldSpec, eventSpec), interfaces.IJSEventHandler, '', handler)
        self._handlers += ((field, event, handler),)

    def getHandlers(self, field):
        """See interfaces.IJSEventHandlers"""
        fieldProvided = zope.interface.providedBy(field)
        handlers = ()
        for event in jsevent.EVENTS:
            eventProvided = zope.interface.providedBy(event)
            handler = self._registry.lookup(
                (fieldProvided, eventProvided), interfaces.IJSEventHandler)
            if handler:
                handlers += ((event, handler),)
        return handlers

    def copy(self):
        """See interfaces.IJSEventHandlers"""
        handlers = JSHandlers()
        for field, event, handler in self._handlers:
            handlers.addHandler(field, event, handler)
        return handlers

    def __add__(self, other):
        """See interfaces.IJSEventHandlers"""
        if not isinstance(other, JSHandlers):
            raise NotImplementedError
        handlers = self.copy()
        for field, event, handler in other._handlers:
            handlers.addHandler(field, event, handler)
        return handlers

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__,
                            [handler for f, e, handler in self._handlers])


class JSHandler(object):
    zope.interface.implements(interfaces.IJSEventHandler)

    def __init__(self, func):
        self.func = func

    def __call__(self, event, selector, request):
        return self.func(selector.widget.form, event, selector)

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.func)


def handler(field, event=jsevent.CLICK):
    """A decorator for defining a javascript event handler."""
    # As a convenience, we also accept form fields to the handler, but get the
    # real field immediately
    if IField.providedBy(field):
        field = field.field
    def createHandler(func):
        handler = JSHandler(func)
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        handlers = f_locals.setdefault('jshandlers', JSHandlers())
        handlers.addHandler(field, event, handler)
        return handler
    return createHandler


@zope.interface.implementer(zope.interface.Interface)
@zope.component.adapter(IAfterWidgetUpdateEvent)
def createSubscriptionsForWidget(event):
    widget = event.widget
    # Only react to widgets that have a field and know the form.
    if not (IFieldWidget.providedBy(widget) and IFormAware.providedBy(widget)):
        return
    # We only have work to do, if there are JS Handlers in the form.
    if not hasattr(widget.form, 'jshandlers'):
        return
    # Step 1: Get the handler.
    handlers = widget.form.jshandlers.getHandlers(widget.field)
    # Step 2: Create a selector.
    selector = WidgetSelector(widget)
    # Step 3: Make sure that the form has JS subscriptions, otherwise add
    #         it.
    if not interfaces.IHaveJSSubscriptions.providedBy(widget.form):
        widget.form.jsSubscriptions = jsevent.JSSubscriptions()
        zope.interface.alsoProvides(
            widget.form, interfaces.IHaveJSSubscriptions)
    # Step 4: Add the subscription to the form:
    for event, handler in handlers:
        widget.form.jsSubscriptions.subscribe(event, selector, handler)
