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
from z3c.form import button, action
from z3c.form.browser.button import ButtonWidget
from z3c.form.interfaces import IFormLayer, IFieldWidget, IFormAware
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

    def update(self):
        super(JSButtonAction, self).update()
        # Step 1: Get the handler.
        handler = self.form.handlers.getHandler(self.field)
        # Step 2: Create a selector.
        selector = WidgetSelector(self)
        # Step 3: Make sure that the form has JS subscriptions, otherwise add
        #         it.
        if not interfaces.IHaveJSSubscriptions.providedBy(self.form):
            self.form.jsSubscriptions = jsevent.JSSubscriptions()
            zope.interface.alsoProvides(
                self.form, interfaces.IHaveJSSubscriptions)
        # Step 4: Add the subscription to the form:
        self.form.jsSubscriptions.subscribe(handler.event, selector, handler)


class JSHandler(object):
    zope.interface.implements(interfaces.IJSEventHandler)

    def __init__(self, button, func, event=jsevent.CLICK):
        self.button = button
        self.func = func
        self.event = event

    def __call__(self, event, selector, request):
        return self.func(selector.widget.form, selector)

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.button)


def handler(field, **kwargs):
    """A decorator for defining a javascript event handler."""
    def createHandler(func):
        handler = JSHandler(field, func, **kwargs)
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        handlers = f_locals.setdefault('handlers', button.Handlers())
        handlers.addHandler(field, handler)
        return handler
    return createHandler


@zope.interface.implementer(zope.interface.Interface)
@zope.component.adapter(IAfterWidgetUpdateEvent)
def createSubscriptionsForWidget(event):
    widget = event.widget
    if not (IFieldWidget.providedBy(widget) and IFormAware.providedBy(widget)):
        return
    # Step 1: Get the handler.
    handler = widget.form.handlers.getHandler(widget.field)
    if handler is None:
        return
    # Step 2: Create a selector.
    selector = WidgetSelector(widget)
    # Step 3: Make sure that the form has JS subscriptions, otherwise add
    #         it.
    if not interfaces.IHaveJSSubscriptions.providedBy(widget.form):
        widget.form.jsSubscriptions = jsevent.JSSubscriptions()
        zope.interface.alsoProvides(
            widget.form, interfaces.IHaveJSSubscriptions)
    # Step 4: Add the subscription to the form:
    widget.form.jsSubscriptions.subscribe(handler.event, selector, handler)
