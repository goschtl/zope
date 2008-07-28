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
"""Form Implementation

$Id: form.py 77154 2007-06-27 19:29:23Z srichter $
"""
__docformat__ = "reStructuredText"
import sys
import zope.interface
import zope.component
import zope.location
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.pagetemplate.interfaces import IPageTemplate
from z3c.form import util
from z3c.form.interfaces import IAfterWidgetUpdateEvent
from z3c.template.interfaces import ILayoutTemplate

from z3c.formsnippet import interfaces
from z3c.formsnippet.i18n import MessageFactory as _


class Formframe(object):
    """A Mixin for Form Frames"""

    frame = None
    errorstatus = None #ViewPageTemplateFile('pt/errorstatus.pt')

    def __call__(self):
        self.update()
        layout = zope.component.getMultiAdapter((self, self.request),
            ILayoutTemplate)
        return layout(self)

    def render(self):
        '''See interfaces.IForm'''
        # render content template
        # Make sure, the frame object has a template that can be called
        # from the frame template

        if self.template is None:
            self.template = zope.component.getMultiAdapter(
                (self, self.request), IPageTemplate)
        
        if self.errorstatus is None:
            self.errorstatus = zope.component.getMultiAdapter(
                (self, self.request), interfaces.IErrorstatusTemplate)

        if self.frame is None:
            self.frame = zope.component.getMultiAdapter(
                (self, self.request), interfaces.IFormframeTemplate)

        return self.frame(self)

class AddFormframe(Formframe):

    def __call__(self):
        self.update()
        if self._finishedAdd:
            self.request.response.redirect(self.nextURL())
            return ''
        layout = zope.component.getMultiAdapter((self, self.request),
            ILayoutTemplate)
        return layout(self)

class Snippet(zope.location.Location):
    """HTML snippets around a widget."""
    zope.interface.implements(interfaces.ISnippets)

    def __init__(self, view):
        self.view = view

    def __getattr__(self, name):
        view = self.view
        snippet = zope.component.getMultiAdapter(
                (view.context, view.request, view.form, view.field, view),
                IPageTemplate, name=name+'_'+view.mode)
        return snippet(self.view)


@zope.component.adapter(IAfterWidgetUpdateEvent)
def addWidgetsnippet(event):
    """instantiates snippets"""
    widget = event.widget
    widget.snippets = Snippet(widget)

class FormframeTemplateFactory(object):
    """Formframe template factory."""

    def __init__(self, filename, contentType='text/html'):
        self.template = ViewPageTemplateFile(filename, content_type=contentType)
    def __call__(self, view, request):
        return self.template.__get__(view, None)


class ErrorstatusTemplateFactory(object):
    """Errorstatus template factory."""

    def __init__(self, filename, contentType='text/html'):
        self.template = ViewPageTemplateFile(filename, content_type=contentType)
    def __call__(self, view, request):
        # FIXME - Return a bound template - not very pretty, but
        # I don't see another solution...
        return self.template.__get__(view, None)


class SnippetTemplateFactory(object):
    """Snippet template factory."""

    def __init__(self, filename, contentType='text/html',
                 context=None, request=None, view=None,
                 field=None, widget=None):
        self.template = ViewPageTemplateFile(filename, content_type=contentType)
        zope.component.adapter(
            util.getSpecification(context),
            util.getSpecification(request),
            util.getSpecification(view),
            util.getSpecification(field),
            util.getSpecification(widget))(self)
        zope.interface.implementer(IPageTemplate)(self)

    def __call__(self, context, request, view, field, widget):
        return self.template

    
