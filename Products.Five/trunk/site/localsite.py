##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Local sites

$Id$
"""
from zope.interface import implements
from zope.component import getGlobalSiteManager
from zope.component.interfaces import ComponentLookupError
from zope.app.component.interfaces import ISite, IPossibleSite
from Acquisition import aq_parent, aq_inner
from Products.Five.site.interfaces import IFiveSiteManager, IFiveUtilityRegistry

class FiveSiteManager(object):
    implements(IFiveSiteManager)

    def __init__(self, context):
        # make {get|query}NextSiteManager() work without having to
        # resort to Zope 2 acquisition
        self.context = self.__parent__ = context
        warnings.warn("The FiveSiteManager is deprecated and will be removed "
                      "in Zope 2.12. \nSee Five/doc/localsite.txt .",
                      DeprecationWarning, 2)

    @property
    def __bases__(self):
        next = self.next
        if next is None:
            return ()
        return (next,)

    @property
    def next(self):
        obj = self.context
        while obj is not None:
            obj = aq_parent(aq_inner(obj))
            if ISite.providedBy(obj):
                return obj.getSiteManager()
        # In Zope 3.1+, returning None here is understood by
        # getNextSiteManager as that our next site manager is the
        # global one. If we returned the global one, it would be
        # understood as a lookup error. Yeah, it's weird, tell me
        # about it.
        return None

    @property
    def adapters(self):
        next = self.next
        if next is None:
            next = getGlobalSiteManager()
        return next.adapters

    @property
    def utilities(self):
        return IFiveUtilityRegistry(self.context)

    def queryAdapter(self, object, interface, name, default=None):
        return self.adapters.queryAdapter(object, interface, name, default)

    def queryMultiAdapter(self, objects, interface, name, default=None):
        return self.adapters.queryMultiAdapter(objects, interface, name, default)

    def getAdapters(self, objects, provided):
        next = self.next
        if next is None:
            next = getGlobalSiteManager()
        return next.getAdapters(objects, provided)

    def subscribers(self, required, provided):
        return self.adapters.subscribers(required, provided)

    def queryUtility(self, interface, name='', default=None):
        return self.utilities.queryUtility(interface, name, default)

    def getUtilitiesFor(self, interface):
        return self.utilities.getUtilitiesFor(interface)

    def getAllUtilitiesRegisteredFor(self, interface):
        return self.utilities.getAllUtilitiesRegisteredFor(interface)

    def registerUtility(self, interface, utility, name=''):
        return self.utilities.registerUtility(interface, utility, name)

class FiveSite:
    implements(IPossibleSite)

    def getSiteManager(self):
        return FiveSiteManager(self)

    def setSiteManager(self, sm):
        raise NotImplementedError('This class has a fixed site manager')


#BBB: Goes away in Five Zope 2.12

import warnings
from Products.Five.component import enableSite, disableSite
from zope.app.component.hooks import setSite, clearSite, setHooks

def enableLocalSiteHook(obj):
    warnings.warn("The enableLocalSiteHook is deprecated and will be removed "
                  "in Zope 2.12. \nSee Five/doc/localsite.txt .",
                  DeprecationWarning, 2)
    enableSite(obj)
    components = FiveSiteManager(obj)
    obj.setSiteManager(components)
    setSite(obj)
    setHooks()

def disableLocalSiteHook(obj):
    """Remove __before_traverse__ hook for Local Site
    """
    warnings.warn("The disableLocalSiteHook is deprecated and will be removed "
                  "in Zope 2.12. \nSee Five/doc/localsite.txt .",
                  DeprecationWarning, 2)
    disableSite(obj)
    clearSite()
    obj.setSiteManager(None)
