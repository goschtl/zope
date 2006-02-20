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
"""Basic components support

$Id$
"""

import zope.interface.adapter
from zope import interface
from zope.component import interfaces
import zope.interface.interfaces

class Components(object):

    def __init__(self, bases=()):
        self._init_registries()
        self._init_registrations()
        self.__bases__ = tuple(bases)

    def _init_registries(self):
        self.adapters = zope.interface.adapter.AdapterRegistry()
        self.utilities = zope.interface.adapter.AdapterRegistry()

    def _init_registrations(self):
        self._utility_registrations = {}
        self._adapter_registrations = {}
        self._subscription_registrations = []
        self._handler_registrations = []


    @apply
    def __bases__():

        def get_bases(self):
            return self.__dict__['__bases__']
        def set_bases(self, bases):
            self.adapters.__bases__ = tuple([
                base.adapters for base in bases])
            self.utilities.__bases__ = tuple([
                base.utilities for base in bases])
            self.__dict__['__bases__'] = bases

        return property(get_bases, set_bases)

    def registerUtility(self, component, provided=None, name=u'', info=u''):
        if provided is None:
            provided = _getUtilityProvided(component)
        self._utility_registrations[(provided, name)] = component, info
        self.utilities.register((), provided, name, component)

    def unregisterUtility(self, component=None, provided=None, name=u''):
        if provided is None:
            if component is None:
                raise TypeError("Must specify one of component and provided")
            provided = _getUtilityProvided(component)

        old = self._utility_registrations.get((provided, name))
        if (old is None) or ((component is not None) and
                             (component != old[0])):
            return False
        
        del self._utility_registrations[(provided, name)]
        self.utilities.unregister((), provided, name)
        return True

    def registeredUtilities(self):
        for ((provided, name), (component, info)
             ) in self._utility_registrations.iteritems():
            yield UtilityRegistration(provided, name, component, info)

    def queryUtility(self, provided, name=u'', default=None):
        return self.utilities.lookup((), provided, name, default)

    def getUtility(self, provided, name=u''):
        utility = self.utilities.lookup((), provided, name)
        if utility is None:
            raise interfaces.ComponentLookupError(provided, name)
        return utility

    def registerAdapter(self, factory, required=None, provided=None, name=u'',
                        info=u''):
        if provided is None:
            provided = _getAdapterProvided(factory)
        required = _getAdapterRequired(factory, required)
        self._adapter_registrations[(required, provided, name)
                                    ] = factory, info
        self.adapters.register(required, provided, name, factory)

    def unregisterAdapter(self, factory=None,
                          required=None, provided=None, name=u'',
                          ):
        if provided is None:
            if factory is None:
                raise TypeError("Must specify one of factory and provided")
            provided = _getAdapterProvided(factory)

        if (required is None) and (factory is None):
            raise TypeError("Must specify one of factory and required")
        
        required = _getAdapterRequired(factory, required)
        old = self._adapter_registrations.get((required, provided, name))
        if (old is None) or ((factory is not None) and
                             (factory != old[0])):
            return False
        
        del self._adapter_registrations[(required, provided, name)]
        self.adapters.unregister(required, provided, name)
        return True
        
    def registeredAdapters(self):
        for ((required, provided, name), (component, info)
             ) in self._adapter_registrations.iteritems():
            yield AdapterRegistration(required, provided, name,
                                      component, info)

    def queryAdapter(self, object, interface, name=u'', default=None):
        return self.adapters.queryAdapter(object, interface, name, default)

    def getAdapter(self, object, interface, name=u''):
        adapter = self.adapters.queryAdapter(object, interface, name)
        if adapter is None:
            raise interfaces.ComponentLookupError(object, interface, name)
        return adapter

    def queryMultiAdapter(self, objects, interface, name=u'', default=None):
        return self.adapters.queryMultiAdapter(
            objects, interface, name, default)

    def getMultiAdapter(self, objects, interface, name=u''):
        adapter = self.adapters.queryMultiAdapter(objects, interface, name)
        if adapter is None:
            raise interfaces.ComponentLookupError(objects, interface, name)
        return adapter

    def getAdapters(self, objects, provided):
        for name, factory in self.adapters.lookupAll(
            map(interface.providedBy, objects),
            provided):
            adapter = factory(*objects)
            if adapter is not None:
                yield name, adapter

    def registerSubscriptionAdapter(self,
                                    factory, required=None, provided=None,
                                    name=u'', info=u''):
        if name:
            raise TypeError("Named subscribers are not yet supported")
        if provided is None:
            provided = _getAdapterProvided(factory)
        required = _getAdapterRequired(factory, required)
        self._subscription_registrations.append(
            (required, provided, name, factory, info)
            )
        self.adapters.subscribe(required, provided, factory)

    def registeredSubscriptionAdapters(self):
        for data in self._subscription_registrations:
            yield SubscriptionRegistration(*data)

    def unregisterSubscriptionAdapter(self, factory=None,
                          required=None, provided=None, name=u'',
                          ):
        if name:
            raise TypeError("Named subscribers are not yet supported")
        if provided is None:
            if factory is None:
                raise TypeError("Must specify one of factory and provided")
            provided = _getAdapterProvided(factory)

        if (required is None) and (factory is None):
            raise TypeError("Must specify one of factory and required")
        
        required = _getAdapterRequired(factory, required)

        if factory is None:
            new = [(r, p, n, f, i)
                   for (r, p, n, f, i)
                   in self._subscription_registrations
                   if not (r == required and p == provided)
                   ]
        else:
            new = [(r, p, n, f, i)
                   for (r, p, n, f, i)
                   in self._subscription_registrations
                   if not (r == required and p == provided and f == factory)
                   ]

        if len(new) == len(self._subscription_registrations):
            return False
        

        self._subscription_registrations = new
        self.adapters.unsubscribe(required, provided)
        return True

    def subscribers(self, objects, provided):
        return self.adapters.subscribers(objects, provided)




    def registerHandler(self,
                        factory, required=None,
                        name=u'', info=u''):
        if name:
            raise TypeError("Named handlers are not yet supported")
        required = _getAdapterRequired(factory, required)
        self._handler_registrations.append(
            (required, name, factory, info)
            )
        self.adapters.subscribe(required, None, factory)

    def registeredHandlers(self):
        for data in self._handler_registrations:
            yield HandlerRegistration(*data)

    def unregisterHandler(self, factory=None, required=None, name=u''):
        if name:
            raise TypeError("Named subscribers are not yet supported")

        if (required is None) and (factory is None):
            raise TypeError("Must specify one of factory and required")
        
        required = _getAdapterRequired(factory, required)

        if factory is None:
            new = [(r, n, f, i)
                   for (r, n, f, i)
                   in self._handler_registrations
                   if r != required
                   ]
        else:
            new = [(r, n, f, i)
                   for (r, n, f, i)
                   in self._handler_registrations
                   if not (r == required and f == factory)
                   ]

        if len(new) == len(self._handler_registrations):
            return False
        
        self._handler_registrations = new
        self.adapters.unsubscribe(required, None)
        return True

    def handle(self, *objects):
        self.adapters.subscribers(objects, None)


def _getUtilityProvided(component):
    provided = list(interface.providedBy(component))
    if len(provided) == 1:
        return provided[0]
    raise TypeError(
        "The utility doesn't provide a single interface "
        "and no provided interface was specified.")

def _getAdapterProvided(factory):
    provided = list(interface.implementedBy(factory))
    if len(provided) == 1:
        return provided[0]
    raise TypeError(
        "The adapter factory doesn't implement a single interface "
        "and no provided interface was specified.")

def _getAdapterRequired(factory, required):
    if required is None:
        try:
            required = factory.__component_adapts__
        except AttributeError:
            raise TypeError(
                "The adapter factory doesn't have a __component_adapts__ "
                "attribute and no required specifications were specified"
                )

    result = []
    for r in required:
        if not zope.interface.interfaces.ISpecification.providedBy(r):
            r = interface.implementedBy(r)
        result.append(r)
    return tuple(result)
        
        
class UtilityRegistration(object):

    def __init__(self, provided, name, component, doc):
        (self.provided, self.name, self.component, self.info
         ) = provided, name, component, doc

    def __repr__(self):
        return '%s(%r, %r, %r, %r)' % (
            self.__class__.__name__,
            getattr(self.provided, '__name__', None), self.name,
            getattr(self.component, '__name__', self.component), self.info,
            )

    def __cmp__(self, other):
        return cmp(self.__repr__(), other.__repr__())
        
class AdapterRegistration(object):

    def __init__(self, required, provided, name, component, doc):
        (self.required, self.provided, self.name, self.factory, self.info
         ) = required, provided, name, component, doc

    def __repr__(self):
        return '%s(%r, %r, %r, %r, %r)' % (
            self.__class__.__name__,
            tuple([r.__name__ for r in self.required]), 
            getattr(self.provided, '__name__', None), self.name,
            getattr(self.factory, '__name__', self.factory), self.info,
            )

    def __cmp__(self, other):
        return cmp(self.__repr__(), other.__repr__())

class SubscriptionRegistration(AdapterRegistration):
    pass

class HandlerRegistration(object):

    def __init__(self, required, name, handler, doc):
        (self.required, self.name, self.handler, self.info
         ) = required, name, handler, doc

    
