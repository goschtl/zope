##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Provide basic browser functionality

$Id$
"""

import Acquisition
from  Acquisition import aq_inner, aq_parent, aq_base
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from interfaces import ITraversable
from zope.interface import implements
from zope.interface.common.mapping import IItemMapping
from zope.component import getView
from zope.component import getViewProviding
from zope.app.traversing.browser.interfaces import IAbsoluteURL


class BrowserView(Acquisition.Explicit):
    security = ClassSecurityInfo()

    def __init__(self, context, request):
        self.context = context
        self.request = request

    # XXX do not create any methods on the subclass called index_html,
    # as this makes Zope 2 traverse into that first!

InitializeClass(BrowserView)

class AbsoluteURL(BrowserView):
    """An adapter for Zope3-style absolute_url using Zope2 methods

    (original: zope.app.traversing.browser.absoluteurl)
    """

    def __init__(self, context, request):
        self.context, self.request = context, request

    implements(IAbsoluteURL)

    def __str__(self):
        context = aq_inner(self.context)
        return context.absolute_url()

    __call__ = __str__

    def breadcrumbs(self):
        context = self.context
        request = self.request

        container = aq_parent(aq_inner(context))
        if container is None or not ITraversable.providedBy(container):
            return ({'name': context.getId(),
                     'url': context.absolute_url()
                     },)

        view = getViewProviding(container, IAbsoluteURL, request)
        base = tuple(view.breadcrumbs())
        name = context.getId()
        base += ({'name': name,
                  'url': ("%s/%s" % (base[-1]['url'], name))
                  },)

        return base


class SiteAbsoluteURL(AbsoluteURL):
    """An adapter for Zope3-style absolute_url using Zope2 methods

    This one is just used to stop breadcrumbs from crumbing up
    to the Zope root.

    (original: zope.app.traversing.browser.absoluteurl)
    """

    def breadcrumbs(self):
        context = self.context
        request = self.request

        return ({'name': context.getId(),
                 'url': context.absolute_url()
                 },)

class Macros:

    implements(IItemMapping)

    macro_pages = ()
    aliases = {
        'view': 'page',
        'dialog': 'page',
        'addingdialog': 'page'
        }

    def __getitem__(self, key):
        key = self.aliases.get(key, key)
        context = self.context
        request = self.request
        for name in self.macro_pages:
            page = getView(context, name, request)
            try:
                v = page[key]
            except KeyError:
                pass
            else:
                return v
        raise KeyError, key

class StandardMacros(BrowserView, Macros): pass
