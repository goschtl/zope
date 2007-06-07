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

from z3c.form import button, util, action, widget
from z3c.form.interfaces import (IButton, IFieldWidget, IValue,
                            IButtonHandlers, IFormLayer, IButtonForm)

import interfaces, jsevent


class ButtonWidget(widget.Widget):
    """A submit button of a form."""
    zope.interface.implementsOnly(interfaces.IButtonWidget)

    css = u'buttonWidget'
    accesskey = None

@zope.component.adapter(IButton, IFormLayer)
@zope.interface.implementer(IFieldWidget)
def SubmitFieldWidget(field, request):
    submit = widget.FieldWidget(field, SubmitWidget(request))
    submit.value = field.title
    return submit


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

    def __call__(self):
        ## TODO: Passing None makes the tests work because the handler
        ## functions take self as the first arg.  Instead of passing
        ## None, I should be passing the form the handler is defined
        ## in - but how do I get this from here?
        return self.func(None)

    def __repr__(self):
        return '<%s for %r>' %(self.__class__.__name__, self.button)


def handler(button, **kwargs):
    """A decoratore for defining a javascript event handler."""
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

    def __init__(self, request, field, name):
        action.Action.__init__(self, request, field.title, name)
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
        return renderer.render(handler, self.id)


class JSButtonActions(util.Manager):
    """JS Button Action Manager class."""
    zope.interface.implementsOnly(interfaces.IJSActions)

    zope.component.adapts(
        IButtonForm,
        zope.interface.Interface,
        zope.interface.Interface)

    __name__ = __parent__ = None

    def __init__(self, form, request, content):
        super(JSButtonActions, self).__init__()
        self.form = form
        self.request = request
        self.content = content

    def update(self):
        """See z3c.form.interfaces.IActions."""
        # Create a unique prefix
        prefix = util.expandPrefix(self.form.prefix)
        prefix += util.expandPrefix(self.form.buttons.prefix)
        for name, button in self.form.buttons.items():
            # Only create an action for the button, if the condition is
            # fulfilled
            if button.condition is not None and not button.condition(self.form):
                continue
            fullName = prefix + name
            buttonAction = JSButtonAction(self.request, button, fullName)
            # Look up a potential custom title for the action.
            title = zope.component.queryMultiAdapter(
                (self.form, self.request, self.content, button, self),
                IValue, name='title')
            if title is not None:
                buttonAction.title = title.get()
            self._data_keys.append(name)
            self._data_values.append(buttonAction)
            self._data[name] = buttonAction
            zope.location.locate(buttonAction, self, name)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)
