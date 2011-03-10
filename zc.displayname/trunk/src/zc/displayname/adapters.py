##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Adapters for the `zc.displayname` package.

$Id: adapters.py 4811 2006-01-17 20:45:52Z fred $
"""

from zope import interface, component, i18n, proxy
from zope.i18nmessageid import Message
from zope.security.interfaces import Unauthorized
import zope.dublincore.interfaces
import zope.location.interfaces
from zope.publisher.interfaces import IRequest
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.browser import BrowserView
from zope.traversing.browser.absoluteurl import absoluteURL
from zope.traversing.interfaces import IContainmentRoot

from zc.displayname import interfaces
from zc.displayname.i18n import _

INSUFFICIENT_CONTEXT = _("There isn't enough context to get URL information. "
                       "This is probably due to a bug in setting up location "
                       "information.")

class DefaultDisplayNameGenerator(BrowserView):
    component.adapts(zope.location.interfaces.ILocation, IRequest)
    interface.implementsOnly(interfaces.IDisplayNameGenerator)

    def __call__(self, maxlength=None):
        ob = self.context
        try:
            try:
                dc = zope.dublincore.interfaces.IDCDescriptiveProperties(ob)
            except TypeError:
                name = ob.__name__
            else:
                name = dc.title or ob.__name__
        except Unauthorized:
            name = ob.__name__ # __name__ should always be available; if it is
            # not, we consider that a configuration error.
        return convertName(name, self.request, maxlength)

class SiteDisplayNameGenerator(BrowserView):
    component.adapts(IContainmentRoot, IRequest)
    interface.implementsOnly(interfaces.IDisplayNameGenerator)

    def __call__(self, maxlength=None):
        return convertName(_('[root]'), self.request, maxlength)

def convertName(name, request, maxlength):
    """trim name to maxlength, if given.  Translate, if appropriate.

    Not appropriate for names with HTML.
    """
    if isinstance(name, Message):
        name = i18n.translate(name, context=request, default=name)
    if maxlength is not None:
        if not isinstance(maxlength, (int, long)):
            raise TypeError('maxlength must be int', maxlength)
        if maxlength < 0:
            raise ValueError('maxlength must be 0 or greater', maxlength)
        name_len = len(name)
        if name_len > maxlength:
            if maxlength < 4:
                name = '?' * maxlength
            else:
                name = name[:maxlength-3] + "..."
    return name

class Breadcrumbs(BrowserView):
    interface.implementsOnly(interfaces.IBreadcrumbs)
    component.adapts(None, IHTTPRequest)

    def __call__(self, maxlength=None):
        context = self.context
        request = self.request
        if proxy.sameProxiedObjects(context, request.getVirtualHostRoot()):
            base = ()
        else:
            container = getattr(context, '__parent__', None)
            if container is None:
                raise TypeError, INSUFFICIENT_CONTEXT
            view = component.getMultiAdapter(
                (container, request), interfaces.IBreadcrumbs)
            base = tuple(view(maxlength))
        name_gen = component.getMultiAdapter(
            (context, request), interfaces.IDisplayNameGenerator)
        url = absoluteURL(context, request)
        return base + (
            {"name_gen": name_gen, "url": url, "name": name_gen(maxlength),
             "object": context},)

class TerminalBreadcrumbs(BrowserView):
    interface.implementsOnly(interfaces.IBreadcrumbs)
    component.adapts(IContainmentRoot, IHTTPRequest) # may adapt others

    def __call__(self, maxlength=None):
        context = self.context
        request = self.request
        name_gen = component.getMultiAdapter(
            (context, request), interfaces.IDisplayNameGenerator)
        url = absoluteURL(context, request)
        return ({"name_gen": name_gen, "url": url, "name": name_gen(maxlength),
                 "object": context},)

class HiddenBreadcrumbs(BrowserView):
    """Breadcrumbs for an object that doesn't want to be in the breadcrumbs"""
    interface.implementsOnly(interfaces.IBreadcrumbs)
    component.adapts(None, IHTTPRequest)

    def __call__(self, maxlength=None):
        context = self.context
        request = self.request
        if proxy.sameProxiedObjects(context, request.getVirtualHostRoot()):
            base = ()
        else:
            container = getattr(context, '__parent__', None)
            if container is None:
                raise TypeError, INSUFFICIENT_CONTEXT
            view = component.getMultiAdapter(
                (container, request), interfaces.IBreadcrumbs)
            base = tuple(view(maxlength))
        return base

@component.adapter(zope.location.interfaces.ILocation, IHTTPRequest)
@interface.implementer(interface.Interface)
def breadcrumbs(context, request):
    "breadcrumbs; unlimited display name length for each traversed object"
    return component.getMultiAdapter(
        (context, request), interfaces.IBreadcrumbs)()

@component.adapter(zope.location.interfaces.ILocation, IHTTPRequest)
@interface.implementer(interface.Interface)
def breadcrumbs20char(context, request):
    "breadcrumbs; display name length limited to 20 characters for each object"
    return component.getMultiAdapter(
        (context, request), interfaces.IBreadcrumbs)(20)
