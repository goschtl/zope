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
"""JQuery-backend implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface

from jquery.layer import IJQueryJavaScriptBrowserLayer

from z3c.formjs import interfaces


class JQueryEventRenderer(object):
    """IJSEventRenderer implementation.

    See ``interfaces.IJSEventRenderer``.
    """
    zope.interface.implements(interfaces.IJSEventRenderer)
    zope.component.adapts(
        interfaces.IJSEvent, IJQueryJavaScriptBrowserLayer)

    def __init__(self, event, request):
        self.request = request
        self.event = event

    def render(self, handler, id, form):
        return '$("#%s").bind("%s", function(){%s});' % (
                          id, self.event.name, handler(form, id))


class JQueryBaseValidationRenderer(object):

    def __init__(self, form, field, request):
        self.form = form
        self.field = field
        self.request = request

    def _ajaxURL(self):
        widget = self.form.widgets[self.field.__name__]
        # build js expression for extracting widget value
        # XXX: Maybe we should adapt the widget to IJSValueExtractorRenderer?
        valueString = '$("#%s").val()' % widget.id

        # build a js expression that joins valueString expression
        queryString = '"?widget-id=%s&%s=" + %s' % (
            widget.id, widget.name, valueString)

        # build a js expression that joins form url, validate path, and query
        # string
        ajaxURL = '"'+self.form.request.getURL() + '/validate" + ' + queryString

        return ajaxURL


class JQueryMessageValidationRenderer(JQueryBaseValidationRenderer):

    zope.interface.implements(interfaces.IJSMessageValidationRenderer)
    zope.component.adapts(interfaces.IAJAXValidator,
                          zope.interface.Interface,
                          IJQueryJavaScriptBrowserLayer)

    def render(self):
        ajaxURL = self._ajaxURL()
        # build a js expression that shows the user the error message
        # XXX: later this should query for a renderer based on the widget
        #     jsrenderer = zope.component.queryMultiAdapter(
        #         (widget, self.request), interfaces.IJSErrorMessageRenderer)
        #     messageSetter = jsrenderer.render()
        messageSetter = 'alert(data);'
        ajax = '$.get(%s,\nfunction(data){\n%s\n})' % (ajaxURL, messageSetter)
        return ajax
