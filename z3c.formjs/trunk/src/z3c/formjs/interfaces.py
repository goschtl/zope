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
from zope.viewlet.interfaces import IViewletManager

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

class ICSSSelector(ISelector):
    """Select a DOM element by a CSS selector expression."""

    expr = zope.schema.TextLine(
        title=u"Expression",
        description=u"CSS selector pointing to a DOM element.",
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

    def __iter__():
        """Return an iterator of all subscriptions."""

    def __getitem__(name):
        """Return all the subscriptions for the handler with the given name."""


class IRenderer(zope.interface.Interface):
    """Render a component in the intended output format."""

    def update():
        """Update renderer."""

    def render():
        """Render content."""

# -----[ Javascript Functions ]----------------------------------------------

class IJSFunction(zope.interface.Interface):
    """A Javascript Function."""

    name = zope.schema.BytesLine(
        title=u"Name",
        description=u"The name of the function.",
        required=True)

    arguments = zope.schema.List(
        title=u"Arguments",
        description=u"A list of arguments of the function.",
        required=True)

    def render():
        """Render the content of the JS function."""

    def call():
        """Render a JavaScript call to the function."""


class IJSFunctions(zope.interface.Interface):
    """A manager of Javascript functions."""

    def add(function, namespace=''):
        """Add a new function to the given namespace."""

    def render(self):
        """Render all functions."""

class IHaveJSFunctions(zope.interface.Interface):
    """An component that has a JS functions manager .

    This component is most often a view component. When rendering a page this
    interface is used to check whether any functions must be rendered.
    """

    jsFunctions = zope.schema.Object(
        title=u"Javascript Functions",
        description=u"Attribute holding the JS Functions Manager.",
        schema = IJSFunctions,
        required=True)

# -----[ JavaScript Viewlet Manager ]-----------------------------------------

class IDynamicJavaScript(IViewletManager):
    """Viewlet manager for dynamically generated javascript."""


# -----[ Widgets ]------------------------------------------------------------

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

    __name__ = zope.schema.ASCIILine(
        title=u"Name",
        description=u"The name of the handler. Like a function's name",
        required=True)

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


# -----[ Widget Mode Switcher ]-----------------------------------------------

class IWidgetModeSwitcher(zope.interface.Interface):
    """A component that enables forms to switch between display and input
    widgets."""

    def getDisplayWidget():
        """Return the rendered display widget.

        The method expects to find a field called 'widget-name' in the request
        containing the short name to the field/widget.
        """

    def getInputWidget():
        """Return the rendered input widget.

        The method expects to find a field called 'widget-name' in the request
        containing the short name to the field/widget.
        """

    def saveWidgetValue():
        """Save the new value of the widget and return any possible errors.

        The method expects to find a field called 'widget-name' in the request
        containing the short name to the field/widget. The request must also
        contain all fields required for the widget to successfully extract the
        value.
        """

class IWidgetSwitcher(zope.interface.Interface):
    """Switches the widhet to another mode."""

    form = zope.schema.Field(
        title=u"Form",
        description=u"The form.",
        required=True)

    widget = zope.schema.Field(
        title=u"Widget",
        description=u"The widget that is being switched.",
        required=True)

    mode = zope.schema.TextLine(
        title=u"Mode",
        description=u"The mode to which to switch to.",
        required=True)

    def render():
        """Render the switcher into JavaScript."""

class ILabelWidgetSwitcher(zope.interface.Interface):
    """Switches the widget to an input widget when clicking on the label."""

    form = zope.schema.Field(
        title=u"Form",
        description=u"The form.",
        required=True)

    mode = zope.schema.TextLine(
        title=u"Mode",
        description=u"The mode to which to switch to.",
        required=True)

    def render():
        """Render the switcher into JavaScript."""


class IWidgetSaver(zope.interface.Interface):
    """Saves a widget's value to the server."""

    form = zope.schema.Field(
        title=u"Form",
        description=u"The form.",
        required=True)

    widget = zope.schema.Field(
        title=u"Widget",
        description=u"The widget for which the value is saved.",
        required=True)

    def render():
        """Render the saver into JavaScript."""


# -----[ AJAX ]--------------------------------------------------------


class IAJAXHandlers(ISelectionManager):
    """Container of AJAX handlers."""


class IAJAXHandler(zope.interface.Interface):

    def __call__(context, request):
        """Return a callable that calls the handler function.

        Return a callable which has access to context and request
        without context and request being passed as arguments.
        """

class IAJAXRequestHandler(zope.interface.Interface):
    """An object that has methods for handling ajax requests."""

    ajaxRequestHandlers = zope.schema.Object(
        title=u"AJAX Request Handlers Manager",
        schema=IAJAXHandlers)


# -----[ Form Traverser ]-------------------------------------------------

class IFormTraverser(zope.interface.Interface):
    """Marker interface for forms that can be traversed by the @@ajax
    view."""



# -----[ Client Side Event System ]---------------------------------------

class IClientEventHandlers(zope.interface.Interface):
    """A collection of client side event handlers for server side events."""

    def addHandler(required, handler):
        """Add a new handler for a the given required interfaces."""

    def getHandler(event):
        """Get the handler for the given server side event."""

    def copy():
        """Copy this object and return the copy."""

    def __add__(other):
        """Add another handlers object.

        During the process a copy of the current handlers object should be
        created and the other one is added to the copy. The return value is
        the copy.
        """

class IClientEventHandler(zope.interface.Interface):
    """A handler managed by the client event handlers."""

    def __call__(self, form, event):
        """Execute the handler."""
