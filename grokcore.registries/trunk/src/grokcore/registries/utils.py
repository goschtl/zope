# -*- coding: utf-8 -*-

import pkg_resources
from zope.component import queryUtility, getSiteManager, getGlobalSiteManager
from zope.component.interfaces import IComponents


def contextualSiteManager():
    return getSiteManager() or getGlobalSiteManager()


def query_registry(name, parent_components=None):
    if parent_components is None:
        parent_components = contextualSiteManager()
    return parent_components.getUtility(IComponents, name)
