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
from zope.interface import implements
from zope.component import getGlobalServices
from zope.component.interfaces import IServiceService, IUtilityService
from zope.app.utility.interfaces import ILocalUtilityService
from zope.component.exceptions import ComponentLookupError
from zope.component.servicenames import Utilities
from zope.app.site.interfaces import ISite
from zope.app.site.interfaces import IPossibleSite
from zope.app.publication.zopepublication import BeforeTraverseEvent
from zope.component.servicenames import Adapters

from interfaces import IFiveSite
from ExtensionClass import Base
from Acquisition import aq_base, aq_inner, aq_parent
from Products.SiteAccess.AccessRule import AccessRule
from ZPublisher.BeforeTraverse import registerBeforeTraverse
from ZPublisher.BeforeTraverse import unregisterBeforeTraverse

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
        raise TypeError, 'Must provide ISite'
    rules = unregisterBeforeTraverse(obj, HOOK_NAME)
    if hasattr(obj, HOOK_NAME):
        delattr(obj, HOOK_NAME)

    directlyProvides(obj, directlyProvidedBy(obj) - ISite)

class LocalService:
    implements(IServiceService)

    def __init__(self, context):
        self.context = context

    def getServiceDefinitions(self):
        """Retrieve all Service Definitions

        Should return a list of tuples (name, interface)
        """
        return getGlobalServices().getServiceDefinitions()

    def getInterfaceFor(self, name):
        """Retrieve the service interface for the given name
        """
        return getGlobalServices().getInterfaceFor(name)

    def getService(self, name):
        """Retrieve a service implementation

        Raises ComponentLookupError if the service can't be found.
        """
        if name in (Utilities,):
            return SimpleLocalUtilityService(self.context)
        return getGlobalServices().getService(name)

class SimpleLocalUtilityService:
    implements(ILocalUtilityService)

    def __init__(self, context):
        self.context = context

    def getUtility(self, interface, name=''):
        """See IUtilityService interface
        """
        c = self.queryUtility(interface, name)
        if c is not None:
            return c
        raise ComponentLookupError(interface, name)

    def queryUtility(self, interface, name='', default=None):
        """See IUtilityService interface
        """
        if name == '':
            # Singletons. Only one per interface allowed, so, let's call it
            # by the interface.
            name = interface.getName()
        utilities = getattr(self.context, 'utilities')
        utility = utilities._getOb(name, None)
        if utility is None:
            return default
        if not interface.providedBy(utility):
            return default
        return utility

    def getUtilitiesFor(self, interface):
        utilities = getattr(self.context, 'utilities')
        for utility in utilities.objectValues():
            if interface.providedBy(utility):
                yield (utility.getId(), utility)

    def getAllUtilitiesRegisteredFor(self, interface):
        # This also supposedly returns "overridden" utilities, but we don't
        # keep them around. It also does not return the name-value pair that
        # getUtilitiesFor returns.
        utilities = getattr(self.context, 'utilities')
        for utility in utilities.objectValues():
            if interface.providedBy(utility):
                yield utility

    def registerUtility(self, interface, utility, name=''):
        # I think you are *really* supposed to:
        # 1. Check if there is a "registrations" object for utilities.
        # 2. If not create one.
        # 3. Get it.
        # 4. Create a registration object for the utility.
        # 5. Rgister the registration object in the registrations.
        # But that is quite complex, and Jim sais he wants to change that
        # anyway, and in any case the way you would normally do this in Zope3
        # and Five would probably differ anyway, so, here is this new 
        # Five-only, easy to use method!
        
        utilities = getattr(self.context, 'utilities', None)
        if utilities is None:
            from OFS.Folder import Folder
            self.context._setObject('utilities', Folder('utilities'))
            utilities = self.context.utilities

        if name == '':
            # Singletons. Only one per interface allowed, so, let's call it
            # by the interface.
            name = interface.getName()
            
        utilities._setObject(name, utility)


class FiveSite:
    implements(IPossibleSite)

    def __init__(self, context):
        self.context = context

    def getSiteManager(self):
        return LocalService(self)

    def setSiteManager(self, sm):
        raise NotImplementedError('This class has a fixed site manager')


from Products.Five.browser import BrowserView

class MakeSite(BrowserView):
    """View for convering a possible site to a site
    """

    def makeSite(self):
        """Convert a possible site to a site"""
        if ISite.providedBy(self.context):
            raise ValueError('This is already a site')

        enableLocalSiteHook(self.context)
        return "This object is now a site"
        