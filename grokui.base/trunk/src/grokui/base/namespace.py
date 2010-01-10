# -*- coding: utf-8 -*-
"""Components to keep Grok UI releated stuff in a dedicated namespace.
"""
import grok

from zope.interface import Interface
from zope.publisher.browser import applySkin
from zope.publisher.interfaces import browser
from zope.app.folder.interfaces import IRootFolder
from zope.traversing.interfaces import ITraversable
from zope.location import LocationProxy

class GrokUILayer(grok.IDefaultBrowserLayer):
    """A basic layer for all Grok UI components.
    """
    pass


class GrokUISkin(GrokUILayer, browser.IBrowserSkinType):
    """A skin for all Grok UI stuff.
    """
    grok.skin('GrokUISkin')


class IGrokuiRealm(Interface):
    def getRoot(self):
        """returns the root folder"""


class GrokUINamespace(grok.MultiAdapter):
    grok.name('grokui')
    grok.provides(ITraversable)
    grok.implements(IGrokuiRealm)
    grok.adapts(IRootFolder, browser.IBrowserRequest)

    def __init__(self, context, request):
        self.root = context
        self.request = request
        applySkin(self.request, GrokUISkin)

    def traverse(self, name, ignore):
        return LocationProxy(self, self.root, "++grokui++")
