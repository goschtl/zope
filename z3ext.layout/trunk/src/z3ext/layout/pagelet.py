##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""

$Id$
"""
import logging, sys
from zope import interface, component
from zope.component import queryUtility, queryAdapter, queryMultiAdapter
from zope.publisher.browser import BrowserPage
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.tales.expressions import SimpleModuleImporter
from zope.app.publisher.browser import queryDefaultViewName

from interfaces import ILayout, IPagelet, IPageletType, IPageletContext


@interface.implementer(IPagelet)
@component.adapter(interface.Interface, interface.Interface)
def queryPagelet(context, request):
    name = queryDefaultViewName(context, request, None)
    if name:
        view = queryMultiAdapter((context, request), name=name)
        if IPagelet.providedBy(view):
            return view


def queryLayout(view, request, context=None, iface=ILayout, name=''):
    if context is None:
        context = view.context

    while context is not None:
        layout = queryMultiAdapter((view, context, request), iface, name)
        if layout is not None:
            return layout

        context = getattr(context, '__parent__', None)

    return None


class BrowserPagelet(BrowserPage):
    interface.implements(IPagelet)

    template = None
    layoutname = u''

    def __init__(self, context, *args):
        request = args[-1]
        super(BrowserPagelet, self).__init__(context, request)

        args = args[:-1]
        self.contexts = args

        for idx in range(len(args)):
            setattr(self, 'context%s'%idx, args[idx])

    def update(self):
        pass

    def render(self):
        if self.template is not None:
            return self.template()
        else:
            template = queryMultiAdapter((self, self.request), IPagelet)
            if template is not None:
                template.update()
                return template.render()
            raise LookupError("Can't find IPagelet for this pagelet.")

    def __call__(self):
        self.update()

        if self.isRedirected or self.request.response.getStatus() in (302, 303):
            return u''

        layout = queryLayout(self, self.request, name=self.layoutname)
        if layout is None:
            return self.render()
        else:
            return layout()

    isRedirected = False

    def redirect(self, url=''):
        if url:
            self.request.response.redirect(url)

        self.isRedirected = True


class PageletPublisher(object):
    interface.implements(IBrowserPublisher)
    component.adapts(interface.Interface, interface.Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.modules = SimpleModuleImporter()

    def publishTraverse(self, request, name):
        try:
            return self[name]
        except KeyError:
            pass

        raise NotFound(self.context, name, request)

    def __call__(self, name=''):
        try:
            return self[name]
        except KeyError:
            pass

        return u''

    def __getitem__(self, name):
        if name:
            iface = queryUtility(IPageletType, name)

            if iface is None:
                try:
                    iface, iname = name.rsplit('.', 1)
                    iface = getattr(self.modules[iface], iname)
                except:
                    raise KeyError(name)
        else:
            iface = IPagelet

        context = self.context

        if iface.providedBy(context):
            return context.render()

        contexts = queryAdapter(context, IPageletContext, name)
        if contexts is not None:
            required = [context]
            if type(contexts) in (list, tuple):
                required.extend(contexts)
            else:
                required.append(contexts)
            required.append(self.request)
            view = queryMultiAdapter(required, iface)
        else:
            view = queryMultiAdapter((context, self.request), iface)

        if view is not None:
            try:
                view.update()
                if view.isRedirected:
                    return u''
                return view.render()
            except Exception, err:
                log = logging.getLogger('z3ext.layout')
                log.exception(err)

        raise KeyError(name)

    def browserDefault(self, request):
        return self.context, ('',)
