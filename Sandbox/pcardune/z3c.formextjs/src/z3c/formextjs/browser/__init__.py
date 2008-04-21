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
"""ExtJS Form Widgets

$Id$
"""
from zope.viewlet.interfaces import IViewletManager
from zope.viewlet.viewlet import ViewletBase
from zope.viewlet.manager import WeightOrderedViewletManager

from z3c.formextjs.browser.pytemplate import PythonTemplateFile

def escape(s):
    s = str(s).replace('\n','\\n').replace("'","\\'")
    return s

def jsSafe(name):
    return str(hash(name)).replace('-','_')


class IJSFormViewletManager(IViewletManager):
    """js form viewlet manager for rendering form generating javascript."""


class ExtJSFormViewletManager(WeightOrderedViewletManager):

    template = PythonTemplateFile('form-viewlet-manager.pyt')

    def render(self):
        return self.template(self)


class FormAwareViewlet(ViewletBase):

    def update(self):
        self.form = self.__parent__

    def hash(self, name):
        return str(hash(name)).replace('-','_')


class ExtJSFormViewlet(FormAwareViewlet):
    """Viewlet for js form declaration."""

    template = PythonTemplateFile('form-viewlet.pyt')

    def render(self):
        return self.template(self)


class ExtJSWidgetsViewlet(FormAwareViewlet):
    """Viewlet that hook in all the widgets."""

    template = PythonTemplateFile('form-widgets-viewlet.pyt')

    def render(self):
        return self.template(self, **globals())


class InputWidgetTemplate(object):
    """provider of IPageTemplate for extjs widgets."""

    template = PythonTemplateFile('form-widget.pyt')

    def __init__(self, context, request, form, field, widget):
        self.context = context
        self.request = request
        self.form = form
        self.field = field
        self.widget = widget

    def __call__(self, widget):
        scope = globals()
        return self.template(widget, **scope)

class TextAreaInputWidget(InputWidgetTemplate):

    template = PythonTemplateFile('text-area-widget.pyt')

## class ExtJSButtonsViewlet(FormAwareViewlet):
##     """Viewlet that add JS hooks for displaying buttons."""

##     template = PythonTemplateFile('form-buttons-viewlet.pyt')

##     def render(self):
##         return self.template(self, **globals())
