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
from zope import interface, component
from zope.component import queryMultiAdapter
from zope.publisher.browser import BrowserPage
from zope.pagetemplate.interfaces import IPageTemplate
from zope.app.publisher.browser import queryDefaultViewName

from z3ext.layout.interfaces import IPagelet, ILayout


@interface.implementer(IPagelet)
@component.adapter(interface.Interface, interface.Interface)
def queryPagelet(context, request):
    name = queryDefaultViewName(context, request, 'index.html')
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

    layoutname = u''

    index = None
    template = None

    def update(self):
        pass

    def render(self):
        template = queryMultiAdapter((self, self.request), IPageTemplate)

        if template is None:
            template = self.template or self.index
            if template is None:
                raise LookupError("Can't find IPageTemplate for pagelet.")
            return template()

        return template(self)

    def __call__(self):
        self.update()

        if self.isRedirected:
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
