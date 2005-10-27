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
from zope.event import notify
from zope.interface import directlyProvides, directlyProvidedBy
from zope.interface import implements
from zope.component import getGlobalSiteManager
from zope.component.interfaces import ISiteManager
from zope.component.exceptions import ComponentLookupError

from zope.app.component.interfaces import ISite, IPossibleSite
from zope.app.publication.zopepublication import BeforeTraverseEvent

from ExtensionClass import Base
from Acquisition import aq_base, aq_inner, aq_parent
from Products.SiteAccess.AccessRule import AccessRule
from ZPublisher.BeforeTraverse import registerBeforeTraverse
from ZPublisher.BeforeTraverse import unregisterBeforeTraverse

from Products.Five.site.interfaces import IFiveUtilityRegistry

# Hook up custom component architecture calls
import zope.app.component.hooks
zope.app.component.hooks.setHooks()

def siteManagerAdapter(ob):
    """An adapter * -> ISiteManager.

    This is registered in place of the one in Zope 3 so that we lookup
    using acquisition instead of ILocation.
    """
    current = ob
    while True:
        if ISite.providedBy(current):
            return current.getSiteManager()
        current = aq_parent(aq_inner(current))
        if current is None:
            # It does not support acquisition or has no parent, so we
            # return the global site
            return getGlobalSiteManager()

HOOK_NAME = '__local_site_hook__'

class LocalSiteHook(Base):
    def __call__(self, container, request):
        notify(BeforeTraverseEvent(container, request))


def enableLocalSiteHook(obj):
    """Install __before_traverse__ hook for Local Site
    """
    # We want the original object, not stuff in between, and no acquisition
    obj = aq_base(obj)
    if not IPossibleSite.providedBy(obj):
        raise TypeError, 'Must provide IPossibleSite'
    hook = AccessRule(HOOK_NAME)
    registerBeforeTraverse(obj, hook, HOOK_NAME, 1)

    if not hasattr(obj, HOOK_NAME):
        setattr(obj, HOOK_NAME, LocalSiteHook())

    directlyProvides(obj, ISite, directlyProvidedBy(obj))

def disableLocalSiteHook(obj):
    """Remove __before_traverse__ hook for Local Site
    """
    # We want the original object, not stuff in between, and no acquisition
    obj = aq_base(obj)
    if not ISite.providedBy(obj):
        raise TypeError, 'Must provide ISite'
    unregisterBeforeTraverse(obj, HOOK_NAME)
    if hasattr(obj, HOOK_NAME):
        delattr(obj, HOOK_NAME)

    directlyProvides(obj, directlyProvidedBy(obj) - ISite)

class FiveSiteManager(object):
    implements(ISiteManager)

    def __init__(self, context):
        self.context = context

    @property
    def adapters(self):
        return getGlobalSiteManager().adapters

    @property
    def utilities(self):
        return IFiveUtilityRegistry(self.context)

    @property
    def next(self):
        obj = self.context
        while obj is not None:
            obj = aq_parent(aq_inner(obj))
            if ISite.providedBy(obj):
                return obj.getSiteManager()

    def queryAdapter(self, object, interface, name, default=None):
        return self.adapters.queryAdapter(object, interface, name, default)

    def queryMultiAdapter(self, objects, interface, name, default=None):
        return self.adapters.queryMultiAdapter(objects, interface, name, default)

    def getAdapters(self, objects, provided):
        return self.adapters.getAdapters(objects, provided)

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
