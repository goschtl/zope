##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""adapter service
"""

__metaclass__ = type
import sys
from zope.interface import implements, providedBy
from zope.interface.adapter import AdapterRegistry
from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IAdapterService
from zope.component.service import GlobalService
import warnings

class IGlobalAdapterService(IAdapterService):

    def register(required, provided, name, factory):
        """Register an adapter factory

        :Parameters:
          - `required`: a sequence of specifications for objects to be
             adapted. 
          - `provided`: The interface provided by the adapter
          - `name`: The adapter name
          - `factory`: The object used to compute the adapter
        """

    def subscribe(required, provided, factory):
        """Register a subscriber factory
        
        :Parameters:
          - `required`: a sequence of specifications for objects to be
             adapted. 
          - `provided`: The interface provided by the adapter
          - `name`: The adapter name
          - `factory`: The object used to compute the subscriber
        """

    def getRegisteredMatching(required=None,
                              provided=None,
                              name=None,
                              with=None):
        """Return information about registered data

        A five-tuple is returned containing:

          - registered name,

          - registered for interface

          - registered provided interface, and

          - registered data
        """

class AdapterService(AdapterRegistry):

    implements(IAdapterService)

    def queryAdapter(self, object, interface, default=None):
        return self.queryNamedAdapter(object, interface, '', default)

    def queryNamedAdapter(self, object, interface, name='', default=None):
        factory = self.lookup1(providedBy(object), interface, name)
        if factory is not None:
            return factory(object)
        
        return default

    def queryMultiAdapter(self, objects, interface, name='', default=None):
        factory = self.lookup(map(providedBy, objects), interface, name)
        if factory is not None:
            return factory(*objects)

        return default

    def subscribers(self, objects, interface):
        subscriptions = self.subscriptions(map(providedBy, objects), interface)
        return [subscription(*objects) for subscription in subscriptions]
    

class GlobalAdapterService(AdapterService, GlobalService):

    implements(IGlobalAdapterService)
