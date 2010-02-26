# -*- coding: utf-8 -*-
"""Components to keep Grok UI related stuff in a dedicated namespace.
"""
import grok
from zope.site.interfaces import IRootFolder
from zope.location import LocationProxy
from zope.component import queryUtility
from zope.publisher.browser import applySkin
from zope.publisher.interfaces import browser
from zope.publisher.interfaces import NotFound
from zope.traversing.interfaces import ITraversable
from grokui.base.interfaces import IGrokUIRealm, IGrokUIPluginInfo


class GrokUILayer(grok.IDefaultBrowserLayer):
    """A basic layer for all Grok UI components.
    """
    pass


class GrokUISkin(GrokUILayer, browser.IBrowserSkinType):
    """A skin for all Grok UI stuff.
    """
    grok.skin('GrokUISkin')


class GrokUINamespace(grok.MultiAdapter):
    grok.name('grokui')
    grok.provides(ITraversable)
    grok.implements(IGrokUIRealm)
    grok.adapts(IRootFolder, browser.IBrowserRequest)

    def __init__(self, context, request):
        self.root = context
        self.request = request
        applySkin(self.request, GrokUISkin)

    def traverse(self, name, ignore):
        return LocationProxy(self, self.root, "++grokui++")


class GrokUIPluginsInfo(grok.MultiAdapter):
    grok.name('info')
    grok.provides(ITraversable)
    grok.adapts(IGrokUIRealm, browser.IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        info = queryUtility(IGrokUIPluginInfo, name=name)
        if info is None:
            raise NotFound(self.context, name, self.request)
        return LocationProxy(info, self.context, '++info++%s' % name)
