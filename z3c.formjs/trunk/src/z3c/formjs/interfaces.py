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
"""Javascript Form Framework Interfaces.

$Id: $
"""
__docformat__ = "reStructuredText"
import zope.interface
import zope.schema

from z3c.form.interfaces import IButton, IButtonHandler, IManager, IWidget
from z3c.form.interfaces import ISelectionManager, IForm


# -----[ Event Subscription ]------------------------------------------------

class IJSEvent(zope.interface.Interface):
    """An interface for javascript event objects."""

    name = zope.schema.TextLine(
        title=u"Event Name",
        description=u"The name of an event (i.e. click/dblclick/changed).",
        required=True)


class ISelector(zope.interface.Interface):
    """An object describing the selection of DOM Elements."""

class IIdSelector(ISelector):
    """Select a DOM element by Id."""

    id = zope.schema.TextLine(
        title=u"Id",
        description=u"Id of the DOM element to be selected.",
        required=True)


class IJSSubscription(zope.interface.Interface):
    """A Subscription within Javascript."""

    event = zope.schema.Object(
        title=u"Event",
        description=u"The event.",
        schema = IJSEvent,
        required=True)

    selector = zope.schema.Object(
        title=u"Selector",
        description=u"The DOM element selector.",
        schema = ISelector,
        required=True)

    handler = zope.schema.Field(
        title=u"Handler",
        description=(u"A callable nneding three argument: event, selector, "
                     u"and request."),
        required=True)


class IJSSubscriptions(zope.interface.Interface):
    """A manager of Javascript event subscriptions."""

    def subscribe(event, selector, handler):
        """Subscribe an event for a DOM element executing the handler's
        result."""

    def __iter__(self):
        """Return an iterator of all subscriptions."""


class IRenderer(zope.interface.Interface):
    """Render a component in the intended output format."""

    def update(self):
        """Update renderer."""

    def render(self):
        """Render content."""

# -----[ Wiidgets ]-----------------------------------------------------------

class IWidgetSelector(ISelector):
    """Select a DOM element using the action."""

    action = zope.schema.Field(
        title=u"Action",
        description=u"The action being selected.",
        required=True)

# -----[ Views and Forms ]----------------------------------------------------

class IHaveJSSubscriptions(zope.interface.Interface):
    """An component that has a subscription manager .

    This component is most often a view component. When rendering a page this
    interface is used to check whether any subscriptions must be rendered.
    """

    jsSubscriptions = zope.schema.Object(
        title=u"Javascript Subscriptions",
        description=u"Attribute holding the JS Subscription Manager.",
        schema = IJSSubscriptions,
        required=True)


# -----[ Buttons and Handlers ]----------------------------------------------


class IJSButton(IButton):
    """A button that just connects to javascript handlers."""


class IJSEventHandler(zope.interface.Interface):
    """An action handler of Javascript events for fields and buttons."""

    def __call__(event, selector, request):
        """Call the handler.

        The result should be a string containing the script to be executed
        when the event occurs on the specified DOM element.

        The event *must* provide the ``IJSEvent`` interface. The selector
        *must* be an ``IWidgetSelector`` component.
        """


class IJSEventHandlers(zope.interface.Interface):
    """Javascript event handlers for fields and buttons."""

    def addHandler(field, event, handler):
        """Add a new handler for the fiven field and event specification.

        The ``field`` and ``event`` arguments can either be instances, classes
        or specifications/interfaces. The handler *must* provide the
        ``IJSEventHandler`` interface.
        """

    def getHandlers(field):
        """Get a list of (event, handler) pairs for the given field.

        The event is a component providing the ``IJSEvent`` interface, and the
        handler is the same component that has been added before.
        """

    def copy():
        """Copy this object and return the copy."""

    def __add__(other):
        """Add another handlers object.

        During the process a copy of the current handlers object should be
        created and the other one is added to the copy. The return value is
        the copy.
        """


# -----[ Validator ]--------------------------------------------------------


class IValidationScript(zope.interface.Interface):
    """Component that renders the script doing the validation."""

    def render():
        """Render the js expression."""

class IMessageValidationScript(IValidationScript):
    """Causes a message to be returned at validation."""


class IAJAXValidator(zope.interface.Interface):
    """A validator that sends back validation data sent from an ajax request."""

    ValidationScript = zope.schema.Object(
        title=u"Validation Script",
        schema=IValidationScript)

    def validate():
        """Return validation data."""
