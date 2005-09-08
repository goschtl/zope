##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Global Site Manager

$Id$
"""
__docformat__ = "reStructuredText"
import types

from zope import interface
from zope.interface import implements, providedBy, implementedBy, declarations
from zope.interface.adapter import AdapterRegistry
from zope.interface.interfaces import ISpecification

from zope.component.interfaces import ISiteManager, IRegistry
from zope.component.interfaces import ComponentLookupError, Invalid


class IGlobalSiteManager(ISiteManager, IRegistry):

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
        tests.
        """


class SiteManager(object):
    """Site Manager implementation"""

    def queryAdapter(self, object, interface, name, default=None):
        """See ISiteManager interface"""
        return self.adapters.queryAdapter(object, interface, name, default)

    def queryMultiAdapter(self, objects, interface, name='', default=None):
        """See ISiteManager interface"""
        return self.adapters.queryMultiAdapter(objects, interface, name,
                                               default)
    
    def getAdapters(self, objects, provided):
        """See ISiteManager interface"""
        result = []
        for name, factory in self.adapters.lookupAll(map(providedBy, objects),
                                                     provided):
            adapter = factory(*objects)
            if adapter is not None:
                result.append((name, adapter))
        return result

    def subscribers(self, required, provided):
        """See ISiteManager interface"""
        return self.adapters.subscribers(required, provided)
    
    def queryUtility(self, interface, name='', default=None):
        """See ISiteManager interface"""
        return self.utilities.lookup((), interface, name, default)

    def getUtilitiesFor(self, interface):
        return self.utilities.lookupAll((), interface)

    def getAllUtilitiesRegisteredFor(self, interface):
        return self.utilities.subscriptions((), interface)


class GlobalSiteManager(SiteManager):
    """Global Site Manager implementation."""

    implements(IGlobalSiteManager)

    def __init__(self, name=None):
        self.__name__ = name
        self._registrations = []
        self.adapters = GlobalAdapterRegistry(self, 'adapters')
        self.utilities = GlobalAdapterRegistry(self, 'utilities')


    def provideAdapter(self, required, provided, name, factory, info=''):
        """Register an adapter

        >>> from zope.interface import Interface
        >>> registry = GlobalSiteManager()
        >>> class R1(Interface):
        ...     pass
        >>> class R2(R1):
        ...     pass
        >>> class P1(Interface):
        ...     pass
        >>> class P2(P1):
        ...     pass

        >>> registry.provideAdapter((R1, ), P2, 'bob', 'c1', 'd1')
        >>> registry.provideAdapter((R1, ), P2,    '', 'c2', 'd2')
        >>> registry.adapters.lookup((R2, ), P1, '')
        'c2'

        >>> registrations = map(repr, registry.registrations())
        >>> registrations.sort()
        >>> for registration in registrations:
        ...    print registration
        AdapterRegistration(('R1',), 'P2', '', 'c2', 'd2')
        AdapterRegistration(('R1',), 'P2', 'bob', 'c1', 'd1')

        Let's make sure that we can also register regular classes for
        adaptation.

        >>> class O1(object):
        ...     pass
        >>> class O2(object):
        ...     pass
        >>> class O3(object):
        ...     def __init__(self, obj1, obj2=None):
        ...         pass

        >>> registry.provideAdapter((O1, ), R1, '', O3)
        >>> registry.queryAdapter(O1(), R1, '').__class__
        <class 'zope.component.site.O3'>

        >>> registry.provideAdapter((O1, O2), R1, '', O3)
        >>> registry.queryMultiAdapter((O1(), O2()), R1, '').__class__
        <class 'zope.component.site.O3'>
        """
        required = tuple(map(_spec, required))

        self._registrations.append(
            AdapterRegistration(required, provided, name, factory, info),
            )

        self.adapters.register(required, provided, name, factory)

    def subscribe(self, required, provided, factory, info=''):
        """Register an subscriptions adapter

        >>> from zope.interface import Interface
        >>> registry = GlobalSiteManager()
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
        >>> subscriptions = map(str,
        ...                     registry.adapters.subscriptions((R2, ), P1))
        >>> subscriptions.sort()
        >>> subscriptions
        ['c1', 'c2']

        >>> registrations = map(repr, registry.registrations())
        >>> registrations.sort()
        >>> for registration in registrations:
        ...    print registration
        SubscriptionRegistration(('R1',), 'P2', 'c1', 'd1')
        SubscriptionRegistration(('R1',), 'P2', 'c2', 'd2')
        """

        required = tuple(map(_spec, required))

        self._registrations.append(
            SubscriptionRegistration(required, provided, factory, info),
            )

        self.adapters.subscribe(required, provided, factory)

    def provideUtility(self, providedInterface, component, name='', info='',
                        strict=True):

        if strict and not providedInterface.providedBy(component):
            raise Invalid("The registered component doesn't implement "
                          "the promised interface.")

        self.utilities.register((), providedInterface, name, component)

        # Also subscribe to support getAllUtilitiesRegisteredFor:
        self.utilities.subscribe((), providedInterface, component)

        self._registrations.append(
            UtilityRegistration(providedInterface, name, component, info),
            )

    def registrations(self):
        return iter(self._registrations)

    def __reduce__(self):
        # Global site managers are pickled as global objects
        return self.__name__

_class_types = (type, types.ClassType)
def _spec(iface_or_class):
    if ISpecification.providedBy(iface_or_class):
        return iface_or_class
    if iface_or_class is None:
        return interface.Interface
    if isinstance(iface_or_class, _class_types):
        return interface.implementedBy(iface_or_class)
    raise TypeError(iface_or_class, ISpecification)


def GAR(siteManager, registryName):
    return getattr(siteManager, registryName)

class GlobalAdapterRegistry(AdapterRegistry):
    """A global adapter registry

    This adapter registry's main purpose is to be picklable in combination
    with a site manager.
    """
    def __init__(self, parent=None, name=None):
       self.__parent__ = parent
       self.__name__ = name
       super(GlobalAdapterRegistry, self).__init__()
    
    def __reduce__(self):
        return GAR, (self.__parent__, self.__name__)


# Global Site Manager Instance
globalSiteManager = GlobalSiteManager('globalSiteManager')

# Register our cleanup with zope.testing.cleanup to make writing unit tests
# simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(lambda : globalSiteManager.__init__(globalSiteManager.__name__))
del addCleanUp



class AdapterRegistration(object):
    """Registration for a simple adapter."""

    def __init__(self, required, provided, name, value, doc=''):
        (self.required, self.provided, self.name, self.value, self.doc
         ) = required, provided, name, value, doc

    def __repr__(self):
        return '%s(%r, %r, %r, %r, %r)' % (
            self.__class__.__name__,
            tuple([getattr(r, '__name__', None) for r in self.required]),
            getattr(self.provided, '__name__', None), self.name,
            self.value, self.doc,
            )

    def __cmp__(self, other):
        return cmp(self.__repr__(), other.__repr__())


class SubscriptionRegistration(object):
    """Registration for a subscription adapter."""

    def __init__(self, required, provided, value, doc):
        (self.required, self.provided, self.value, self.doc
         ) = required, provided, value, doc

    def __repr__(self):
        return '%s(%r, %r, %r, %r)' % (
            self.__class__.__name__,
            tuple([getattr(r, '__name__', None) for r in self.required]),
            getattr(self.provided, '__name__', None), self.value, self.doc,
            )

    def __cmp__(self, other):
        return cmp(self.__repr__(), other.__repr__())


class UtilityRegistration(object):

    def __init__(self, provided, name, component, doc):
        (self.provided, self.name, self.component, self.doc
         ) = provided, name, component, doc

    def __repr__(self):
        return '%s(%r, %r, %r, %r)' % (
            self.__class__.__name__,
            getattr(self.provided, '__name__', None), self.name,
            getattr(self.component, '__name__', self.component), self.doc,
            )

    def __cmp__(self, other):
        return cmp(self.__repr__(), other.__repr__())

