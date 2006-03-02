##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Component browser views

$Id$
"""
from zope.event import notify
from zope.interface import alsoProvides, noLongerProvides
from zope.app.publication.zopepublication import BeforeTraverseEvent
from zope.app.component.interfaces import ISite, IPossibleSite

import ExtensionClass
from Acquisition import aq_base
from Products.SiteAccess.AccessRule import AccessRule
from ZPublisher.BeforeTraverse import registerBeforeTraverse
from ZPublisher.BeforeTraverse import unregisterBeforeTraverse

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
        current = getattr(current, '__parent__', aq_parent(aq_inner(current)))
        if current is None:
            # It does not support acquisition or has no parent, so we
            # return the global site
            return getGlobalSiteManager()


class LocalSiteHook(ExtensionClass.Base):

    def __call__(self, container, request):
        notify(BeforeTraverseEvent(container, request))

HOOK_NAME = '__local_site_hook__'

def enableSite(obj, iface=ISite):
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

    alsoProvides(obj, iface)

def disableSite(obj, iface=ISite):
    """Remove __before_traverse__ hook for Local Site
    """
    # We want the original object, not stuff in between, and no acquisition
    obj = aq_base(obj)
    if not iface.providedBy(obj):
        raise TypeError('Object must be a site.')

    unregisterBeforeTraverse(obj, HOOK_NAME)
    if hasattr(obj, HOOK_NAME):
        delattr(obj, HOOK_NAME)

    noLongerProvides(obj, iface)
