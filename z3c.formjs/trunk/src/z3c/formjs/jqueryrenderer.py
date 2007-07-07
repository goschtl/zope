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


class JQueryIdSelectorRenderer(object):
    zope.interface.implements(interfaces.IRenderer)
    zope.component.adapts(
        interfaces.IIdSelector, IJQueryJavaScriptBrowserLayer)

    def __init__(self, selector, request):
        self.selector = selector

    def update(self):
        pass

    def render(self):
        return u'#' + self.selector.id


class JQuerySubscriptionRenderer(object):
    zope.interface.implements(interfaces.IRenderer)
    zope.component.adapts(
        interfaces.IJSSubscription, IJQueryJavaScriptBrowserLayer)

    def __init__(self, subscription, request):
        self.subscription = subscription
        self.request = request

    def update(self):
        self.selectorRenderer = zope.component.getMultiAdapter(
            (self.subscription.selector, self.request), interfaces.IRenderer)
        self.selectorRenderer.update()

    def render(self):
        return u'$("%s").bind("%s", function(){%s});' %(
            self.selectorRenderer.render(),
            self.subscription.event.name,
            self.subscription.handler(
                self.subscription.event,
                self.subscription.selector,
                self.request) )


class JQuerySubscriptionsRenderer(object):
    zope.interface.implements(interfaces.IRenderer)
    zope.component.adapts(
        interfaces.IJSSubscriptions, IJQueryJavaScriptBrowserLayer)

    def __init__(self, manager, request):
        self.manager = manager
        self.request = request

    def update(self):
        self.renderers = []
        for subscription in self.manager:
            renderer = zope.component.getMultiAdapter(
                (subscription, self.request), interfaces.IRenderer)
            renderer.update()
            self.renderers.append(renderer)

    def render(self):
        return '$(document).ready(function(){\n  %s\n})' %(
            '\n  '.join([r.render() for r in self.renderers]) )


class JQueryBaseValidationScriptRenderer(object):
    zope.interface.implements(interfaces.IRenderer)

    def __init__(self, script, request):
        self.script = script
        self.request = request

    def _ajaxURL(self):
        widget = self.script.widget
        form = self.script.form
        # build js expression for extracting widget value
        valueString = '$("#%s").val()' % widget.id
        # build a js expression that joins valueString expression
        queryString = '"?widget-name=%s&%s=" + %s' % (
            widget.__name__, widget.name, valueString)
        # build a js expression that joins form url, validate path, and query
        # string
        ajaxURL = '"'+form.request.getURL() + '/validate" + ' + queryString

        return ajaxURL


class JQueryMessageValidationScriptRenderer(JQueryBaseValidationScriptRenderer):
    zope.component.adapts(
        interfaces.IMessageValidationScript, IJQueryJavaScriptBrowserLayer)

    def render(self):
        ajaxURL = self._ajaxURL()
        # build a js expression that shows the user the error message
        # XXX: later this should query for a renderer based on the widget
        #     jsrenderer = zope.component.queryMultiAdapter(
        #         (widget, self.request), interfaces.IJSErrorMessageRenderer)
        #     messageSetter = jsrenderer.render()
        messageSetter = 'if (data != "") { alert(data); }'
        ajax = '$.get(%s,\nfunction(data){\n%s\n})' % (ajaxURL, messageSetter)
        return ajax
