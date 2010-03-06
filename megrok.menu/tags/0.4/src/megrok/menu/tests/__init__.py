
# -*- coding: utf-8 -*-

import zope.component
from zope.component.interfaces import IComponentLookup
from zope.component.testlayer import ZCMLFileLayer
from zope.interface import Interface
from zope.site.folder import rootFolder
from zope.site.site import LocalSiteManager, SiteManagerAdapter


class MegrokMenuLayer(ZCMLFileLayer):

    def setUp(self):
        ZCMLFileLayer.setUp(self)

        # Set up site manager adapter
        zope.component.provideAdapter(
            SiteManagerAdapter, (Interface,), IComponentLookup)

        # Set up site
        site = rootFolder()
        site.setSiteManager(LocalSiteManager(site))
        zope.component.hooks.setSite(site)

        return site

    def tearDown(self):
        ZCMLFileLayer.tearDown(self)
        zope.component.hooks.resetHooks()
        zope.component.hooks.setSite()
