##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Machinery for making things traversable through adaptation

$Id$
"""
from zExceptions import NotFound
from zope.event import notify
from zope.exceptions import NotFoundError
from zope.component import getView, ComponentLookupError
from zope.interface import implements
from zope.interface import directlyProvides, directlyProvidedBy
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.security.management import thread_local
from zope.app.site.interfaces import ISite
from zope.app.traversing.interfaces import ITraverser, ITraversable
from zope.app.traversing.adapters import DefaultTraversable
from zope.app.traversing.adapters import traversePathElement
from zope.app.publication.zopepublication import BeforeTraverseEvent
from monkey import DebugFlags
from interfaces import IFiveSite

from Globals import MessageDialog
from AccessControl import getSecurityManager
from ExtensionClass import Base
from Products.SiteAccess.AccessRule import AccessRule
from ZPublisher.BeforeTraverse import registerBeforeTraverse
from ZPublisher.BeforeTraverse import unregisterBeforeTraverse

_marker = object

class FakeRequest:
    implements(IBrowserRequest)

    debug = DebugFlags()

    def getPresentationSkin(self):
        return None

    def has_key(self, key):
        return False

def newInteraction():
    """Con Zope 3 to use Zope 2's checkPermission.

    Zope 3 when it does a checkPermission will turn around and
    ask the thread local interaction for the checkPermission method.
    By making the interaction *be* Zope 2's security manager, we can
    con Zope 3 into using Zope 2's checker...
    """
    if getattr(thread_local, 'interaction', None) is None:
        thread_local.interaction = getSecurityManager()

class Traversable:
    """A mixin to make an object traversable using an ITraverser adapter.
    """
    __five_traversable__ = True

    def __fallback_traverse__(self, REQUEST, name):
        """Method hook for fallback traversal

        This method is called by __bobo_traverse___ when Zope3-style
        ITraverser traversal fails.

        Just raise a AttributeError to indicate traversal has failed
        and let Zope do it's job.
        """
        raise AttributeError, name

    def __bobo_traverse__(self, REQUEST, name):
        """Hook for Zope 2 traversal

        This method is called by Zope 2's ZPublisher upon traversal.
        It allows us to trick it into faking the Zope 3 traversal system
        by using an ITraverser adapter.
        """
        if not IBrowserRequest.providedBy(REQUEST):
            # Try to get the REQUEST by acquisition
            REQUEST = getattr(self, 'REQUEST', None)
            if not IBrowserRequest.providedBy(REQUEST):
                REQUEST = FakeRequest()
        # con Zope 3 into using Zope 2's checkPermission
        newInteraction()
        try:
            return ITraverser(self).traverse(
                path=[name], request=REQUEST).__of__(self)
        except (ComponentLookupError, NotFoundError,
                AttributeError, KeyError, NotFound):
            pass
        try:
            return getattr(self, name)
        except AttributeError:
            pass
        try:
            return self[name]
        except (AttributeError, KeyError):
            pass
        return self.__fallback_traverse__(REQUEST, name)
    __bobo_traverse__.__five_method__ = True


class FiveTraversable(DefaultTraversable):

    def traverse(self, name, furtherPath):
        context = self._subject
        __traceback_info__ = (context, name, furtherPath)
        # Find the REQUEST
        REQUEST = getattr(context, 'REQUEST', None)
        if not IBrowserRequest.providedBy(REQUEST):
            REQUEST = FakeRequest()
        # Try to lookup a view first
        try:
            return getView(context, name, REQUEST)
        except ComponentLookupError:
            pass
        # If a view can't be found, then use default traversable
        return super(FiveTraversable, self).traverse(name, furtherPath)

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

HOOK_NAME = '__local_site_hook__'

class LocalSiteHook(Base):

    meta_type = 'Five Local Site Hook'

    def __call__(self, container, request):
        notify(BeforeTraverseEvent(container, request))


def manage_addLocalSiteHook(self, REQUEST=None, **ignored):
    """Install __before_traverse__ hook for Local Site
    """
    # We want the original object, not stuff in between, and no acquisition
    self = self.this()
    self = getattr(self, 'aq_base', self)

    hook = AccessRule(HOOK_NAME)
    registerBeforeTraverse(self, hook, HOOK_NAME, 1)

    if not hasattr(self, HOOK_NAME):
        setattr(self, HOOK_NAME, LocalSiteHook())

    directlyProvides(self, ISite, directlyProvidedBy(self))

    if REQUEST is not None:
        return MessageDialog(
            title='Local Site Hook',
            message='Local Site Hook has been enabled for this object',
            action='%s/manage_main' % REQUEST['URL1'])

def manage_removeLocalSiteHook(self, REQUEST=None, **ignored):
    """Remove __before_traverse__ hook for Local Site
    """
    # We want the original object, not stuff in between, and no acquisition
    self = self.this()
    self = getattr(self, 'aq_base', self)

    rules = unregisterBeforeTraverse(self, HOOK_NAME)
    if hasattr(self, HOOK_NAME):
        delattr(self, HOOK_NAME)

    if REQUEST is not None:
        return MessageDialog(
            title='Local Site Hook',
            message='Local Site Hook has been disabled for this object',
            action='%s/manage_main' % REQUEST['URL1'])
