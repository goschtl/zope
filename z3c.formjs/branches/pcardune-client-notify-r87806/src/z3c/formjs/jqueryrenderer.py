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
from zope.traversing.browser import absoluteURL
from zope.component.interfaces import IObjectEvent
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.viewlet.viewlet import ViewletBase

from z3c.formjs import interfaces

try:
    # try to be backwards compatible.
    from jquery.layer import IJQueryJavaScriptBrowserLayer
    IBaseLayer = IJQueryJavaScriptBrowserLayer
except ImportError:
    IBaseLayer = IBrowserRequest

class IJQueryLayer(IBaseLayer):
    """Layer for the jquery renderers."""

class JQueryViewlet(ViewletBase):
    """A viewlet that grabs the jquery libraries from google."""

    def render(self):
        return '<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.2.6/jquery.min.js"></script>'

class JQueryIdSelectorRenderer(object):
    zope.interface.implements(interfaces.IRenderer)
    zope.component.adapts(
        interfaces.IIdSelector, IJQueryLayer)

    def __init__(self, selector, request):
        self.selector = selector

    def update(self):
        pass

    def render(self):
        return u'#' + self.selector.id


class JQueryCSSSelectorRenderer(object):
    zope.interface.implements(interfaces.IRenderer)
    zope.component.adapts(
        interfaces.ICSSSelector, IJQueryLayer)

    def __init__(self, selector, request):
        self.selector = selector

    def update(self):
        pass

    def render(self):
        return self.selector.expr


class JQuerySubscriptionRenderer(object):
    zope.interface.implements(interfaces.IRenderer)
    zope.component.adapts(
        interfaces.IJSSubscription, IJQueryLayer)

    def __init__(self, subscription, request):
        self.subscription = subscription
        self.request = request

    def update(self):
        self.selectorRenderer = zope.component.getMultiAdapter(
            (self.subscription.selector, self.request), interfaces.IRenderer)
        self.selectorRenderer.update()

    def render(self):
        return u'$("%s").bind("%s", function(event){%s});' %(
            self.selectorRenderer.render(),
            self.subscription.event.name,
            self.subscription.handler(
                self.subscription.event,
                self.subscription.selector,
                self.request) )


class JQuerySubscriptionsRenderer(object):
    zope.interface.implements(interfaces.IRenderer)
    zope.component.adapts(
        interfaces.IJSSubscriptions, IJQueryLayer)

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
        parts = [r.render() for r in self.renderers]
        if parts:
            return '$(document).ready(function(){\n  %s\n})' %(
                '\n  '.join(parts) )
        else:
            return ''

class JQueryObjectEventRenderer(object):
    zope.component.adapts(IObjectEvent,
                          IJQueryLayer)
    zope.interface.implements(interfaces.IRenderer)

    def __init__(self, event, request):
        self.event = event
        self.request = request

    def update(self):
        pass

    def render(self):
        attrs = set([])
        for interface in zope.interface.providedBy(self.event):
            attrs.update(interface.names())
        content = '[{%s}]' % ','.join(['"%s":"%s"' % (attr,escape(getattr(self.event, attr)))
                                       for attr in attrs])
        return content

def escape(s):
    s = unicode(s)
    return s.replace('"','\\"').replace("'","\\'")


class JQueryNotifyClientHandlerRenderer(object):
    zope.component.adapts(interfaces.INotifyClientHandler,
                          IJQueryLayer)
    zope.interface.implements(interfaces.IRenderer)

    def __init__(self, handler, request):
        self.handler = handler
        self.request = request

    def update(self):
        pass

    def render(self):
        renderer = zope.component.queryMultiAdapter(
            (self.handler.event, self.request), interfaces.IRenderer)
        if renderer is not None:
            renderer.update()
            event = renderer.render()
        else:
            event = '{}'
        result = '$()'
        for interface in zope.interface.providedBy(self.handler.event):
            eventName = '"%s.%s"' % (interface.__module__,
                                     interface.__name__)
            result+='\n.trigger(%s, %s)' % (eventName, event)
        result += ';'
        return result


class JQueryMessageValidationScriptRenderer(object):
    zope.component.adapts(
        interfaces.IMessageValidationScript, IJQueryLayer)
    zope.interface.implements(interfaces.IRenderer)

    function = 'applyErrorMessage'

    def __init__(self, script, request):
        self.context = script
        self.request = request

    def _ajaxURL(self):
        widget = self.context.widget
        form = self.context.form
        # build js expression for extracting widget value
        valueString = '$("#%s").val()' % widget.id
        # build a js expression that joins valueString expression
        queryString = '"?widget-name=%s&%s=" + %s' % (
            widget.__name__, widget.name, valueString)
        # build a js expression that joins form url, validate path, and query
        # string
        ajaxURL = '"'+form.request.getURL() + '/@@ajax/validate" + ' \
                  + queryString

        return ajaxURL

    def update(self):
        pass

    def render(self):
        ajaxURL = self._ajaxURL()
        # build a js expression that shows the user the error message
        widget = self.context.widget
        messageSetter = '%s("%s", msg)' % (self.function, widget.id)
        ajax = '$.get(%s,\nfunction(msg){%s}\n)' % (ajaxURL, messageSetter)
        return ajax


class JQueryWidgetSwitcherRenderer(object):
    zope.component.adapts(
        interfaces.IWidgetSwitcher, IJQueryLayer)
    zope.interface.implements(interfaces.IRenderer)

    function = 'switchWidget'

    def __init__(self, switcher, request):
        self.context = switcher
        self.request = request

    def _ajaxURL(self):
        widget = self.context.widget
        form = self.context.form
        # build a js expression that joins valueString expression
        queryString = '?widget-name=%s' % widget.__name__
        mode = self.context.mode.title()
        # build a js expression that joins form url, validate path, and query
        # string
        ajaxURL = '"'+ absoluteURL(form, form.request) + '/@@ajax/get' \
                  + mode + 'Widget' + queryString + '"'

        return ajaxURL

    def update(self):
        pass

    def render(self):
        ajaxURL = self._ajaxURL()
        widget = self.context.widget
        switcherCall = '%s("%s", "%s", html)' % (
            self.function, widget.id, self.context.mode)
        return '$.get(%s,\nfunction(html){%s}\n)' % (ajaxURL, switcherCall)


class JQueryLabelWidgetSwitcherRenderer(object):
    zope.component.adapts(
        interfaces.ILabelWidgetSwitcher, IJQueryLayer)
    zope.interface.implements(interfaces.IRenderer)

    function = 'switchWidget'
    widgetIdExpr = 'event.target.parentNode.attributes["for"].value'

    def __init__(self, switcher, request):
        self.context = switcher
        self.request = request

    def _ajaxURL(self):
        # build a js expression that joins valueString expression
        queryString = '?widget-id=' + self.widgetIdExpr
        mode = self.context.mode.title()
        # build a js expression
        return '"%s/@@ajax/get%sWidget?widget-id=" + %s' % (
            self.request.getURL(), mode, self.widgetIdExpr)

    def update(self):
        pass

    def render(self):
        ajaxURL = self._ajaxURL()
        switcherCall = '%s(%s, "%s", html)' % (
            self.function, self.widgetIdExpr, self.context.mode)
        return '$.get(%s,\nfunction(html){%s}\n)' % (ajaxURL, switcherCall)


class JQueryWidgetSaverRenderer(object):
    zope.component.adapts(
        interfaces.IWidgetSaver, IJQueryLayer)
    zope.interface.implements(interfaces.IRenderer)

    function = 'saveWidget'

    def __init__(self, switcher, request):
        self.context = switcher
        self.request = request

    def _ajaxURL(self):
        widget = self.context.widget
        form = self.context.form
        # build js expression for extracting widget value
        valueString = '$("#%s").val()' % widget.id
        # build a js expression that joins valueString expression
        queryString = '?widget-name=%s&%s=" + %s' % (
            widget.__name__, widget.name, valueString)
        # build a js expression that joins form url, validate path, and query
        # string
        ajaxURL = '"'+ absoluteURL(form, form.request) + \
                  '/@@ajax/saveWidgetValue' + queryString

        return ajaxURL

    def update(self):
        pass

    def render(self):
        ajaxURL = self._ajaxURL()
        widget = self.context.widget
        saveCall = '%s("%s", msg)' % (self.function, widget.id)
        switchCall = 'if (error == false) {%s}' %self.context.switcher.render()
        return '$.get(%s,\nfunction(msg){error=%s; %s}\n)' % (
            ajaxURL, saveCall, switchCall)
