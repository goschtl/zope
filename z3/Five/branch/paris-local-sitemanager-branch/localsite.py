##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""
$Id: traversable.py 9776 2005-03-15 09:18:43Z dreamcatcher $
"""

from zope.event import notify
from zope.interface import directlyProvides, directlyProvidedBy
from zope.component.exceptions import ComponentLookupError
from zope.app.site.interfaces import ISite
from zope.app.site.interfaces import IPossibleSite
from zope.app.publication.zopepublication import BeforeTraverseEvent

from interfaces import IFiveSite
from ExtensionClass import Base
from Acquisition import aq_base, aq_inner, aq_parent
from Products.SiteAccess.AccessRule import AccessRule
from ZPublisher.BeforeTraverse import registerBeforeTraverse
from ZPublisher.BeforeTraverse import unregisterBeforeTraverse

class FiveSite:

    def getSiteManager(self):
        adapted = IFiveSite(self, None)
        if adapted is None:
            return None
        return adapted.getSiteManager()

    def setSiteManager(self, sm):
        adapted = IFiveSite(self, None)
        if adapted is None:
            return None
        return adapted.setSiteManager(sm)

def serviceServiceAdapter(ob):
    """An adapter * -> IServiceService.

    This is registered in place of the one in Zope 3 so that we lookup
    using acquisition instead of ILocation.
    """
    current = ob
    while True:
        if ISite.providedBy(current):
            return current.getSiteManager()
        current = aq_parent(aq_inner(current))
        if current is None:
            raise ComponentLookupError("Could not adapt %r to"
                                       " IServiceService" % (ob, ))

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
        raise TypeError, 'Must provide IPossibleSite'
    rules = unregisterBeforeTraverse(obj, HOOK_NAME)
    if hasattr(obj, HOOK_NAME):
        delattr(obj, HOOK_NAME)

    directlyProvides(obj, directlyProvidedBy(obj) - ISite)
