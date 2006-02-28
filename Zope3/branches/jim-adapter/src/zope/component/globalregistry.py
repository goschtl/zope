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
"""Global components support

$Id$
"""
import types
from zope.interface import implements
from zope.interface.adapter import AdapterRegistry
from zope.deprecation.deprecation import deprecate, deprecated
from zope.component.components import Components
from zope.component.interfaces import Invalid, IComponentLookup, IRegistry
from zope.interface.interfaces import ISpecification

def GAR(components, registryName):
    return getattr(components, registryName)

class GlobalAdapterRegistry(AdapterRegistry):
    """A global adapter registry

    This adapter registry's main purpose is to be picklable in combination
    with a site manager."""

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name
        super(GlobalAdapterRegistry, self).__init__()

    def __reduce__(self):
        return GAR, (self.__parent__, self.__name__)

def NGC(components, registryName):
    return components.getUtility(IComponents, registryName)

########################################################################
#
# BBB 2006/02/28 -- to be removed after 12 months

class IGlobalSiteManager(IComponentLookup, IRegistry):

    def provideAdapter(required, provided, name, factory, info=''):
        """Register an adapter factory

        :Parameters:
          - `required`: a sequence of specifications for objects to be
             adapted.
          - `provided`: The interface provided by the adapter
          - `name`: The adapter name
          - `factory`: The object used to compute the adapter
          - `info`: Provide some info about this particular adapter.
        """

    def subscribe(required, provided, factory, info=''):
        """Register a subscriber factory

        :Parameters:
          - `required`: a sequence of specifications for objects to be
             adapted.
          - `provided`: The interface provided by the adapter
          - `name`: The adapter name
          - `factory`: The object used to compute the subscriber
          - `info`: Provide some info about this particular adapter.
        """

    def provideUtility(providedInterface, component, name='', info='',
                       strict=True):
        """Register a utility

        If strict is true, then the specified component *must* implement the
        `providedInterface`. Turning strict off is particularly useful for
        tests."""

deprecated("IGlobalSiteManager", "The IGlobalSiteManager interface has been "
           "deprecated and will be removed.  Use the zope.component.interfaces."
           "IComponents instead")
#
########################################################################


class BaseGlobalComponents(Components):
    implements(IGlobalSiteManager)

    def __init__(self, name=''):
        self.__name__ = name
        super(BaseGlobalComponents, self).__init__()

    def _init_registries(self):
        self.adapters = GlobalAdapterRegistry(self, 'adapters')
        self.utilities = GlobalAdapterRegistry(self, 'utilities')

    def __reduce__(self):
        # Global site managers are pickled as global objects
        return self.__name__

    ####################################################################
    #
    # BBB 2006/02/28 -- to be removed after 12 months

    @deprecate("The provideAdapter method of the global site manager has been "
               "deprecated. Use registerAdapter instead.")
    def provideAdapter(self, required, provided, name, factory, info=''):
        self.registerAdapter(factory, required, provided, name, info)

    @deprecate("The subscribe method of the global site manager has been "
               "deprecated. Use registerHandler instead.")
    def subscribe(self, required, provided, factory, info=''):
        # we're discarding 'provided' here, but a subscriber doesn't
        # need that anyway
        self.registerHandler(factory, required, u'', info)

    @deprecate("The provideUtility method of the global site manager has been "
               "deprecated. Use registerUtility instead.")
    def provideUtility(self, providedInterface, component, name='', info='',
                       strict=True):
        if strict and not providedInterface.providedBy(component):
            raise Invalid("The registered component doesn't provide "
                          "the promised interface.")

        self.registerUtility(component, providedInterface, name, info)

    @deprecate("The registrations method of the global site manager has been "
               "deprecate. Use either registeredAdapters, registeredUtilities, "
               "or registeredSubscriptionAdapters instead.")
    def registrations(self):
        for reg in self.registeredAdapters():
            yield reg
        for reg in self.registeredSubscriptionAdapters():
            yield reg
        for reg in self.registeredHandlers():
            yield reg
        for reg in self.registeredUtilities():
            yield reg
    #
    ####################################################################    

def _resetBase():
    # globally available singleton
    global base
    base = BaseGlobalComponents('base')

from zope.testing.cleanup import addCleanUp
addCleanUp(_resetBase)
del addCleanUp

# set it up for the first time
_resetBase()

class NamedGlobalComponents(BaseGlobalComponents):

    def __init__(self, parent, name):
        self.__parent__ = parent
        super(NamedGlobalComponents, self).__init__(name)

    def __reduce__(self):
        return NGC, (self.__parent__, self.__name__)
