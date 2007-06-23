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

import zope.schema
import zope.interface
import zope.location
import zope.component
from zope.app.pagetemplate import ViewPageTemplateFile

from z3c.form import button, util, action, widget
from z3c.form.interfaces import (IButton, IFieldWidget, IValue,
                            IButtonHandlers, IFormLayer, IButtonForm)

from jquery.layer import IJQueryJavaScriptBrowserLayer

import interfaces, jsevent


class ButtonWidget(widget.Widget):
    """A submit button of a form."""
    zope.interface.implementsOnly(interfaces.IButtonWidget)

    css = u'buttonWidget'
    accesskey = None
    template = ViewPageTemplateFile("browser/button_input.pt")

@zope.component.adapter(IButton, IJQueryJavaScriptBrowserLayer)
@zope.interface.implementer(IFieldWidget)
def ButtonFieldWidget(field, request):
    button = widget.FieldWidget(field, ButtonWidget(request))
    button.value = field.title
    return button


class JSButton(button.Button):
    """A simple javascript button in a form."""
    zope.interface.implements(interfaces.IJSButton)


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
            (buttonSpec,), interfaces.IJSButtonHandler, '', handler)
        self._handlers += ((button, handler),)

    def getHandler(self, button):
        """See z3c.form.interfaces.IButtonHandlers"""
        buttonProvided = zope.interface.providedBy(button)
        return self._registry.lookup1(buttonProvided, interfaces.IJSButtonHandler)


class Handler(object):
    zope.interface.implements(interfaces.IJSButtonHandler)

    def __init__(self, button, func, event=jsevent.CLICK):
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
        handler = Handler(button, func, event=kwargs.get('event', jsevent.CLICK))
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        jshandlers = f_locals.setdefault('jshandlers', Handlers())
        jshandlers.addHandler(button, handler)
        return handler
    return createHandler


class JSButtonAction(action.Action, ButtonWidget, zope.location.Location):
    zope.interface.implements(IFieldWidget)
    zope.component.adapts(
        IJQueryJavaScriptBrowserLayer,
        interfaces.IJSButton)

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

    def eventHandler(self):
        actions = self.__parent__
        handler = actions.form.jshandlers.getHandler(self.field)
        if handler is None:
            return
        renderer = zope.component.getMultiAdapter((handler.event, self.request),
                                                  interfaces.IJSEventRenderer)
        return renderer.render(handler, self.id, self.__parent__.form)
