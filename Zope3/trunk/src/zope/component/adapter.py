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

from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IAdapterService, IComponentRegistry
from zope.component.service import GlobalService
from zope.interface.adapter import AdapterRegistry
from zope.interface import implements, providedBy, Interface
import sys
import warnings
import zope.schema

class IGlobalAdapterService(IAdapterService, IComponentRegistry):

    def register(required, provided, name, factory, info=''):
        """Register an adapter factory

        :Parameters:
          - `required`: a sequence of specifications for objects to be
             adapted. 
          - `provided`: The interface provided by the adapter
          - `name`: The adapter name
          - `factory`: The object used to compute the adapter
        """

    def subscribe(required, provided, factory, info=''):
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

    def __init__(self):
        AdapterRegistry.__init__(self)
        self._registrations = {}

    def register(self, required, provided, name, factory, info=''):
        """Register an adapter

        >>> registry = GlobalAdapterService()
        >>> class R1(Interface):
        ...     pass
        >>> class R2(R1):
        ...     pass
        >>> class P1(Interface):
        ...     pass
        >>> class P2(P1):
        ...     pass
        
        >>> registry.register((R1, ), P2, 'bob', 'c1', 'd1')
        >>> registry.register((R1, ), P2,    '', 'c2', 'd2')
        >>> registry.lookup((R2, ), P1, '')
        'c2'

        >>> registrations = list(registry.registrations())
        >>> registrations.sort()
        >>> for registration in registrations:
        ...    print registration
        AdapterRegistration(('R1',), 'P2', '', 'c2', 'd2')
        AdapterRegistration(('R1',), 'P2', 'bob', 'c1', 'd1')
        
        """
        required = tuple(required)
        self._registrations[(required, provided, name)] = AdapterRegistration(
            required, provided, name, factory, info)
        
        AdapterService.register(self, required, provided, name, factory)
    
    def subscribe(self, required, provided, factory, info=''):
        """Register an subscriptions adapter

        >>> registry = GlobalAdapterService()
        >>> class R1(Interface):
        ...     pass
        >>> class R2(R1):
        ...     pass
        >>> class P1(Interface):
        ...     pass
        >>> class P2(P1):
        ...     pass
        
        >>> registry.subscribe((R1, ), P2, 'c1', 'd1')
        >>> registry.subscribe((R1, ), P2, 'c2', 'd2')
        >>> subscriptions = list(registry.subscriptions((R2, ), P1))
        >>> subscriptions.sort()
        >>> subscriptions
        ['c1', 'c2']

        >>> registrations = list(registry.registrations())
        >>> registrations.sort()
        >>> for registration in registrations:
        ...    print registration
        SubscriptionRegistration(('R1',), 'P2', 'c1', 'd1')
        SubscriptionRegistration(('R1',), 'P2', 'c2', 'd2')
        
        """
        required = tuple(required)

        registration = SubscriptionRegistration(
            required, provided, factory, info)
        
        self._registrations[(required, provided)] = (
            self._registrations.get((required, provided), ())
            +
            (registration, )
            )

        AdapterService.subscribe(self, required, provided, factory)

    def registrations(self):
        for registration in self._registrations.itervalues():
            if isinstance(registration, tuple):
                for r in registration:
                    yield r
            else:
                yield registration

class AdapterRegistration(object):

    def __init__(self, required, provided, name, value, doc):
        self.required = required
        self.provided = provided
        self.name = name
        self.value = value
        self.doc = doc

    def __repr__(self):
        return '%s(%r, %r, %r, %r, %r)' % (
            self.__class__.__name__,
            tuple([getattr(r, '__name__', None) for r in self.required]),
            self.provided.__name__, self.name,
            self.value, self.doc,
            )

    def __cmp__(self, other):
        if self.__class__ != other.__class__:
            return cmp(repr(self.__class__), repr(other.__class__))
        
        return cmp(
            (self.required, self.provided, self.name,
             self.value, self.doc),
            (other.required, other.provided, other.name,
             other.value, other.doc),
            )

class SubscriptionRegistration(object):

    def __init__(self, required, provided, value, doc):
        self.required = required
        self.provided = provided
        self.value = value
        self.doc = doc

    def __repr__(self):
        return '%s(%r, %r, %r, %r)' % (
            self.__class__.__name__,
            tuple([getattr(r, '__name__', None) for r in self.required]),
            self.provided.__name__, self.value, self.doc,
            )

    def __cmp__(self, other):
        if self.__class__ != other.__class__:
            return cmp(repr(self.__class__), repr(other.__class__))

        return cmp(
            (self.required, self.provided, self.value, self.doc),
            (other.required, other.provided, other.value, other.doc),
            )
