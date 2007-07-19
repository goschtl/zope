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
"""Common z3c.formks test setups

$Id: $
"""
__docformat__ = 'restructuredtext'
import os.path
import zope.component
import zope.interface
from zope.app.pagetemplate import viewpagetemplatefile
from zope.app.testing import setup
from zope.publisher.interfaces.browser import IBrowserRequest

import z3c.formjs.tests
from z3c.formjs import interfaces

class IdSelectorRenderer(object):
    zope.interface.implements(interfaces.IRenderer)
    zope.component.adapts(interfaces.IIdSelector, IBrowserRequest)

    def __init__(self, selector, request):
        self.selector = selector

    def update(self):
        pass

    def render(self):
        return u'#' + self.selector.id

class CSSSelectorRenderer(object):
    zope.interface.implements(interfaces.IRenderer)
    zope.component.adapts(interfaces.ICSSSelector, IBrowserRequest)

    def __init__(self, selector, request):
        self.selector = selector

    def update(self):
        pass

    def render(self):
        return unicode(self.selector.expr)

class SubscriptionRenderer(object):
    zope.interface.implements(interfaces.IRenderer)
    zope.component.adapts(interfaces.IJSSubscription, IBrowserRequest)

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

class ManagerRenderer(object):
    zope.interface.implements(interfaces.IRenderer)
    zope.component.adapts(interfaces.IJSSubscriptions, IBrowserRequest)

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


class MessageValidationScriptRenderer(object):
    zope.interface.implements(interfaces.IRenderer)
    zope.component.adapts(
        interfaces.IMessageValidationScript, IBrowserRequest)

    def __init__(self, script, request):
        self.script = script
        self.request = request

    def render(self):
        return "$.get('/validate', function(data){ alert(data) })"


def setupRenderers():
    zope.component.provideAdapter(IdSelectorRenderer)
    zope.component.provideAdapter(SubscriptionRenderer)
    zope.component.provideAdapter(ManagerRenderer)
    zope.component.provideAdapter(MessageValidationScriptRenderer)


def addTemplate(form, filename):
    path = os.path.join(os.path.dirname(z3c.formjs.tests.__file__), filename)
    form.template = viewpagetemplatefile.BoundPageTemplate(
        viewpagetemplatefile.ViewPageTemplateFile(path), form)


def getPath(filename):
    return os.path.join(os.path.dirname(browser.__file__), filename)

def setUp(test):
    setup.placelessSetUp(test)

def tearDown(test):
    setup.placelessTearDown(test)
