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


from zope.interface import Interface
from zope import schema

from z3c.form.interfaces import IButton, IButtonHandler, IManager, IWidget

class IJSEvent(Interface):
    """A marker interface for javascript event objects."""

    name = schema.TextLine(
        title=u"Event Name",
        description=u"The name of an event (i.e. click/dblclick/changed).",
        required=True)


class IJSEventRenderer(Interface):
    """A renderer that produces javascript code for connecting DOM elements
    to events.
    """

    event = schema.Object(
        title=u"The type of event to be rendered.",
        schema=IJSEvent,
        required=True)

    def render(handler, id, form):
        """render javascript to link DOM element with given id to the
        code produced by the given handler.
        """


class IJSButton(IButton):
    """A button that just connects to javascript handlers."""


class IButtonWidget(IWidget):
    """Button widget."""


class IJSButtonHandler(IButtonHandler):
    """A button handler for javascript buttons."""

    def __call__(form, id):
        """call the handler, passing it the form."""


class IJSAction(Interface):
    """Action"""

    __name__ = schema.TextLine(
        title=u'Name',
        description=u'The object name.',
        required=False,
        default=None)

    title = schema.TextLine(
        title=u'Title',
        description=u'The action title.',
        required=True)


class IJSActions(IManager):
    """A action manager"""

    def update():
        """Setup actions."""
