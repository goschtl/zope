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
"""adapters for shortcuts and target proxies

$Id: adapters.py 4818 2006-01-17 21:01:47Z fred $
"""
import urllib
from zope import interface, component, event
import zope.proxy
from zope.security.proxy import removeSecurityProxy
import zope.publisher.interfaces.browser
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.http import IHTTPRequest

from zope.location.pickling import locationCopy
from zope.dublincore.interfaces import IZopeDublinCore
from zope.lifecycleevent import ObjectCopiedEvent, ObjectCreatedEvent
from zope.size.interfaces import ISized
from zope.traversing.interfaces import ITraversable, IContainmentRoot
from zope.publisher.browser import BrowserView
from zope import copypastemove
from zope.app.container.constraints import checkObject
from zope.app.container.interfaces import INameChooser, IContainer

import zc.displayname.interfaces
from zc.displayname.adapters import INSUFFICIENT_CONTEXT

from zc.shortcut import interfaces, proxy, Shortcut
from zc.shortcut.i18n import _

_safe = '@+' # Characters that we don't want to have quoted

class MetaAdapter:
    """A helper that makes it easy for shortcuts to delegate adapters."""
    def __init__(self, i):
        self.interface = i

    def __call__(self, shortcut):
        return self.interface(shortcut.target, None)

ShortcutSizedAdapterFactory = MetaAdapter(ISized)
ShortcutZopeDoublinCoreAdapterFactory = MetaAdapter(IZopeDublinCore)

@component.adapter(interfaces.IShortcut, zope.publisher.interfaces.IRequest)
@interface.implementer(ITraversable)
def ShortcutTraversalAdapterFactory(shortcut, request):
    return component.getMultiAdapter((shortcut.target, request),
                                       ITraversable, 'view')

@component.adapter(interfaces.IShortcut, zope.publisher.interfaces.IRequest)
@interface.implementer(interface.Interface)
def ShortcutZMIIconFactory(shortcut, request):
    return component.queryMultiAdapter(
        (shortcut.target, request), name='zmi_icon')


def traverseTargetProxiedObject(object, request, name):
    if zope.publisher.interfaces.IPublishTraverse.providedBy(object):
        traverser = object
    else:
        # we have to do a careful dance in order to avoid looking up 
        # ourselves.
        site = component.getSiteManager()
        adapters = site.adapters # IAdapterRegistry
        required = (interface.providedBy(proxy.removeProxy(object)),
                    interface.providedBy(request))
        provided = zope.publisher.interfaces.IPublishTraverse
        lookup_name = ''
        factory = adapters.lookup(required, provided, lookup_name)
        traverser = factory(object, request)
    res = traverser.publishTraverse(request, name)
    res = removeSecurityProxy(res) # this is necessary because otherwise
    # code elsewhere (such as in our security machinery) cannot remove security
    # proxies as it expects to because they are hidden within shortcut proxies.
    if interfaces.IShortcut.providedBy(res):
        res = proxy.ShortcutProxy(res, object, res.__name__)
    else:
        res = proxy.Proxy(res, object, res.__name__)
    return res

class ShortcutPublishTraverseAdapter(object):
    interface.implements(zope.publisher.interfaces.browser.IBrowserPublisher)
    component.adapts(interfaces.IShortcut, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context

    def browserDefault(self, request):
        ob = self.context.target
        adapter = component.getMultiAdapter(
            (ob, request),
            zope.publisher.interfaces.browser.IBrowserPublisher)
        return adapter.browserDefault(request)

    def publishTraverse(self, request, name):
        return traverseTargetProxiedObject(self.context.target, request, name)

class ProxyPublishTraverseAdapter(object):
    interface.implements(zope.publisher.interfaces.IPublishTraverse)
    component.adapts(interfaces.ITraversalProxy, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context

    def publishTraverse(self, request, name):
        context = self.context
        if interfaces.IShortcut.providedBy(context):
            # optimization for a proxied shortcut;
            # it also removes a source of problematic security proxies.
            context = context.target
        return traverseTargetProxiedObject(context, request, name)

@component.adapter(None, IHTTPRequest)
@interface.implementer(interface.Interface)
def traversedURL(ob, request):
    return str(zope.component.getMultiAdapter((ob, request),
                                              interfaces.ITraversedURL))

class TraversedURL(BrowserView):
    interface.implementsOnly(interfaces.ITraversedURL)
    component.adapts(interfaces.ITraversalProxy, IHTTPRequest)

    def __unicode__(self):
        return urllib.unquote(self.__str__()).decode('utf-8')

    def __str__(self):
        context = self.context
        request = self.request

        # The application URL contains all the namespaces that are at the
        # beginning of the URL, such as skins, virtual host specifications and
        # so on.
        if zope.proxy.sameProxiedObjects(
            context, request.getVirtualHostRoot()):
            return request.getApplicationURL()
        parent = context.__traversed_parent__
        if parent is None:
            raise TypeError, INSUFFICIENT_CONTEXT
        url = str(zope.component.getMultiAdapter((parent, request),
                                                 interfaces.ITraversedURL))
        name = context.__traversed_name__
        if name is None:
            raise TypeError, INSUFFICIENT_CONTEXT
        if name:
            url += '/' + urllib.quote(name.encode('utf-8'), _safe)
        return url

class FallbackTraversedURL(BrowserView):
    interface.implementsOnly(interfaces.ITraversedURL)
    component.adapts(interface.Interface, IHTTPRequest)

    def __unicode__(self):
        return urllib.unquote(self.__str__()).decode('utf-8')

    def __str__(self):
        context = self.context
        request = self.request
        # The application URL contains all the namespaces that are at the
        # beginning of the URL, such as skins, virtual host specifications and
        # so on.
        if zope.proxy.sameProxiedObjects(
            context, request.getVirtualHostRoot()):
            return request.getApplicationURL()
        parent = getattr(context, '__parent__', None)
        if parent is None:
            raise TypeError, INSUFFICIENT_CONTEXT
        url = str(zope.component.getMultiAdapter((parent, request),
                                                 interfaces.ITraversedURL))
        name = getattr(context, '__name__', None)
        if name is None:
            raise TypeError, INSUFFICIENT_CONTEXT
        if name:
            url += '/' + urllib.quote(name.encode('utf-8'), _safe)
        return url

class RootTraversedURL(BrowserView):
    interface.implementsOnly(interfaces.ITraversedURL)
    component.adapts(IContainmentRoot, IHTTPRequest)

    def __unicode__(self):
        return urllib.unquote(self.__str__()).decode('utf-8')

    def __str__(self):
        context = self.context
        request = self.request
        if zope.proxy.sameProxiedObjects(
            context, request.getVirtualHostRoot()):
            return request.getApplicationURL()
        url = request.getApplicationURL()
        name = getattr(context, '__name__', None)
        if name:
            url += '/' + urllib.quote(name.encode('utf-8'), _safe)
        return url

class Breadcrumbs(BrowserView):
    interface.implementsOnly(zc.displayname.interfaces.IBreadcrumbs)
    component.adapts(interfaces.ITraversalProxy, IHTTPRequest)

    def __call__(self, maxlength=None):
        context = self.context
        request = self.request
        if zope.proxy.sameProxiedObjects(
            context, request.getVirtualHostRoot()):
            base = ()
        else:
            container = context.__traversed_parent__
            view = component.getMultiAdapter(
                (container, request), zc.displayname.interfaces.IBreadcrumbs)
            base = tuple(view(maxlength))
        name_gen = component.getMultiAdapter(
            (context, request),
            zc.displayname.interfaces.IDisplayNameGenerator)
        url = traversedURL(context, request)
        return base + (
            {"name_gen": name_gen, "url": url, "name": name_gen(maxlength), 
             "object": context},)

# this will probably never be used, because targets are the things for which
# we generally get display names (in breadcrumbs, for instance).  Included
# for completeness.
@component.adapter(
    interfaces.IShortcut, zope.publisher.interfaces.IRequest)
@interface.implementer(zc.displayname.interfaces.IDisplayNameGenerator)
def ShortcutDisplayNameGenerator(context, request):
    return component.getMultiAdapter(
            (context.target, request),
            zc.displayname.interfaces.IDisplayNameGenerator)

# cutcopypaste

class ObjectCopier(copypastemove.ObjectCopier):
    """This is identical to the usual object copier, except that if the object
    is supposed to be created in a repository, it will be copied there and
    place a shortcut to the new object in context."""

    interface.implements(copypastemove.IObjectCopier)
    component.adapts(interface.Interface)

    def copyTo(self, target, new_name=None):
        obj = self.context
        container = obj.__parent__
        orig_name = obj.__name__
        if new_name is None:
            new_name = orig_name
        chooser = INameChooser(target)
        new_name = chooser.chooseName(new_name, obj)
        if not self.copyableTo(target, new_name):
            raise interface.Invalid(
                "Not copyableTo target with name", target, new_name)
        copy = locationCopy(obj)
        copy.__parent__ = copy.__name__ = None
        event.notify(ObjectCopiedEvent(copy, obj))
        repository = component.queryAdapter(
            copy, IContainer, interfaces.REPOSITORY_NAME)
        if repository is not None:
            chooser = INameChooser(repository)
            repo_name = chooser.chooseName(new_name, copy)
            checkObject(repository, repo_name, copy)
            repository[repo_name] = copy
            shortcut = Shortcut(repository[repo_name]) # __getitem__ gets the 
            # ContainedProxy, if it was used
            event.notify(ObjectCreatedEvent(shortcut))
            target[new_name] = shortcut
        else:
            target[new_name] = copy
        return new_name

# link interface.

class ObjectLinkerAdapter(object):

    interface.implements(interfaces.IObjectLinker)
    component.adapts(interface.Interface)

    def __init__(self, context):
        self.context = context

    def linkTo(self, target, new_name=None):
        obj = self.context
        container = obj.__parent__
        orig_name = obj.__name__
        if new_name is None:
            new_name = orig_name
        chooser = INameChooser(target)
        sc = self._createShortcut(obj)
        new_name = chooser.chooseName(new_name, sc)
        if not self.linkableTo(target, new_name):
            raise interface.Invalid(
                "Not linkableTo target with name", target, new_name)
        event.notify(ObjectCreatedEvent(sc))
        target[new_name] = sc
        return new_name

    def linkable(self):
        return True

    def linkableTo(self, target, name=None):
        if name is None:
            name = self.context.__name__
        try:
            checkObject(target, name, self._createShortcut(self.context))
        except interface.Invalid:
            return False
        return True

    def _createShortcut(self, target):
        return Shortcut(target)


class ShortcutLinkerAdapter(object):
    """Linker that generates links based on shortcuts.

    Links created are copies of the original shortcuts, so have any
    associated attribute annotations or other information provided by
    specialized shortcut implementations.  The resulting shortcut is
    not expected to be associated with the original shortcut in any
    way, and refers directly to the target of the original shortcut.

    """

    interface.implements(interfaces.IObjectLinker)
    component.adapts(interfaces.IShortcut)

    def __init__(self, context):
        self.context = context
        self.copier = copypastemove.IObjectCopier(removeSecurityProxy(context))

    def linkTo(self, target, new_name=None):
        try:
            return self.copier.copyTo(target, new_name)
        except interface.Invalid, e:
            raise interface.Invalid("Not linkableTo target with name",
                                    target, e.args[2])

    def linkable(self):
        return self.copier.copyable()

    def linkableTo(self, target, name=None):
        return self.copier.copyableTo(target, name)


# extra tricks

class ObjectCopierLinkingAdapter(object):
    """An object copier adapter that actually makes shortcuts, not clones"""
    
    interface.implements(copypastemove.IObjectCopier)
    # component.adapts deliberately not set; this is expected to be registered
    # for certain specific interfaces.

    def __init__(self, context):
        self.context = context

    def copyTo(self, target, new_name=None):
        obj = self.context
        container = obj.__parent__
        orig_name = obj.__name__
        if new_name is None:
            new_name = orig_name
        chooser = INameChooser(target)
        sc = Shortcut(obj)
        new_name = chooser.chooseName(new_name, sc)
        if not self.copyableTo(target, new_name):
            raise interface.Invalid(
                "Not copyableTo target with name", target, new_name)
        # the shortcut is created, not copied
        event.notify(ObjectCreatedEvent(sc))
        target[new_name] = sc
        return new_name

    def copyable(self):
        return True

    def copyableTo(self, target, name=None):
        if name is None:
            name = self.context.__name__
        try:
            checkObject(target, name, Shortcut(self.context))
        except interface.Invalid:
            return False
        return True
