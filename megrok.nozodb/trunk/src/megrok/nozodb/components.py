# -*- coding: utf-8 -*-

import grok
import grokcore.site
from zope import component, site, location


class ApplicationRoot(grok.GlobalUtility):
    grok.implements(
        grokcore.site.interfaces.IApplication,
        grok.interfaces.IContext,
        location.ILocation,
        component.interfaces.ISite)
    grok.provides(site.interfaces.IRootFolder)
    grok.baseclass()

    __name__ = None
    __parent__ = None

    def getSiteManager(self):
        gsm = component.getGlobalSiteManager()
        return gsm

    def setSiteManager(self, sm):
        pass
