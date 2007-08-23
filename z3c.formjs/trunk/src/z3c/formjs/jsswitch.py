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
"""Switching between display and edit mode.

$Id$
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.schema.interfaces
from z3c.form import button
from z3c.form.interfaces import IWidgets, DISPLAY_MODE
from zope.publisher.interfaces import NotFound

from z3c.formjs import ajax, interfaces, jsevent, jsaction


class WidgetSwitcher(object):
    zope.interface.implements(interfaces.IWidgetSwitcher)

    def __init__(self, form, widget, mode):
        self.form = form
        self.widget = widget
        self.mode = mode

    def render(self):
        renderer = zope.component.getMultiAdapter(
            (self, self.form.request), interfaces.IRenderer)
        return renderer.render()


class WidgetSaver(object):
    zope.interface.implements(interfaces.IWidgetSaver)

    def __init__(self, form, widget):
        self.form = form
        self.widget = widget

    def render(self):
        renderer = zope.component.getMultiAdapter(
            (self, self.form.request), interfaces.IRenderer)
        return renderer.render()


class WidgetModeSwitcher(ajax.AJAXRequestHandler):
    """A mix-in to forms to allow switching between widget modes."""
    zope.interface.implements(interfaces.IWidgetModeSwitcher)
    buttons = button.Buttons()
    mode = DISPLAY_MODE

    @jsaction.handler(zope.schema.interfaces.IField, jsevent.CLICK)
    def switchToInputWidget(self, event, selector):
        return WidgetSwitcher(self, selector.widget, 'input').render()

    @jsaction.handler(zope.schema.interfaces.IField, jsevent.BLUR)
    def switchToDisplayWidget(self, event, selector):
        return u';\n'.join((
            WidgetSaver(self, selector.widget).render(),
            WidgetSwitcher(self, selector.widget, 'display').render()
            ))

    def _getWidget(self, mode):
        # Step 1: Determine the name of the widget.
        shortName = self.request.form['widget-name']
        # Step 2: Limit the form fields only to this one widget.
        self.fields = self.fields.select(shortName)
        # Step 3: Instantiate the widget manager, set the correct mode and
        #         update it.
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        self.widgets.mode = mode
        self.widgets.update()
        # Step 4: Return the widget
        return self.widgets[shortName]

    @ajax.handler
    def getDisplayWidget(self):
        '''See interfaces.IWidgetModeSwitcher'''
        widget = self._getWidget('display')
        handlers = dict(widget.form.jshandlers.getHandlers(widget.field))
        code = handlers[jsevent.CLICK](
            jsevent.CLICK, jsaction.WidgetSelector(widget), self.request)
        widget.onclick = unicode(code.replace('\n', ' '))
        return widget.render()

    @ajax.handler
    def getInputWidget(self):
        '''See interfaces.IWidgetModeSwitcher'''
        widget = self._getWidget('input')
        handlers = dict(widget.form.jshandlers.getHandlers(widget.field))
        code = handlers[jsevent.BLUR](
            jsevent.BLUR, jsaction.WidgetSelector(widget), self.request)
        widget.onblur = unicode(code.replace('\n', ' '))
        return widget.render()

    @ajax.handler
    def saveWidgetValue(self):
        '''See interfaces.IWidgetModeSwitcher'''
        widget = self._getWidget('input')
        data, errors = self.extractData()
        if errors:
            return errors[0].message
        self.applyChanges(data)
        return ''

