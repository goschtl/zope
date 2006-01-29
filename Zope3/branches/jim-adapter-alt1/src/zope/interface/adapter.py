##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Adapter management

$Id$
"""

import weakref
from zope.interface import providedBy, Interface, ro

class readproperty(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, inst, class_):
        if inst is None:
            return self

        func = self.func
        return func(inst)
    

_delegated = ('lookup', 'queryMultiAdapter', 'lookup1', 'queryAdapter',
              'adapter_hook', 'lookupAll', 'names',
              'subscriptions', 'subscribers')

_marker = object
class AdapterRegistry(object):

    def __init__(self, bases=()):
        self._adapters = []
        self._subscribers = []
        self._provided = {}
        self._init_non_persistent()
        self.__bases__ = bases

    def _init_non_persistent(self):
        self._v_subregistries = weakref.WeakKeyDictionary()
        self._v_lookup = lookup = AdapterLookup(self)
        for name in _delegated:
            self.__dict__[name] = getattr(lookup, name)

    def __getstate__(self):
        state = super(AdapterRegistry, self).__getstate__().copy()
        for name in _delegated:
            state.pop(name, 0)
        return state

    def __setstate__(self, state):
        super(AdapterRegistry, self).__setstate__(state)
        self._init_non_persistent()

    @apply
    def __bases__():
        
        def get(self):
            return self.__dict__['__bases__']

        def set(self, v):
            old = self.__dict__.get('__bases__', ())
            for r in old:
                if r not in v:
                    r._removeSubregistry(self)
            for r in v:
                if r not in old:
                    r._addSubregistry(self)
            
            self.__dict__['__bases__'] = v
            self.ro = ro.ro(self)
            self.changed()
            
        return property(get, set)

    def _addSubregistry(self, r):
        self._v_subregistries[r] = 1

    def _removeSubregistry(self, r):
        if r in self._v_subregistries:
            del self._v_subregistries[r]

    def changed(self):
        try:
            lookup = self._v_lookup
        except AttributeError:
            pass
        else:
            lookup.changed()

        for sub in self._v_subregistries.keys():
            sub.changed()
       
    @readproperty
    def _v_extendors(self):
        _v_extendors = {}
        for provided in self._provided:
            for i in provided.__iro__:
                extendors = _v_extendors.get(i, ())
                if provided not in extendors:
                    _v_extendors[i] = (
                        [e for e in extendors if provided.isOrExtends(e)]
                        +
                        [provided]
                        + 
                        [e for e in extendors if not provided.isOrExtends(e)]
                        )
        self._v_extendors = _v_extendors
        return self._v_extendors

    def register(self, required, provided, name, value):
        if value is None:
            self.unregister(required, provided, name, value)
            return

        required = tuple(map(_convert_None_to_Interface, required))
        name = _normalize_name(name)
        order = len(required)
        byorder = self._adapters
        while len(byorder) <= order:
            byorder.append({})
        components = byorder[order]
        key = required + (provided,)
        
        for k in key:
            d = components.get(k)
            if d is None:
                d = {}
                components[k] = d
            components = d

        if components.get(name) == value:
            return
        
        components[name] = value

        n = self._provided.get(provided, 0) + 1
        self._provided[provided] = n
        if n == 1 and '_v_extendors' in self.__dict__:
            del self.__dict__['_v_extendors']

        self.changed()
        
    def unregister(self, required, provided, name, value=None):
        required = tuple(map(_convert_None_to_Interface, required))
        order = len(required)
        byorder = self._adapters
        if order >= len(byorder):
            return False
        components = byorder[order]
        key = required + (provided,)
        
        for k in key:
            d = components.get(k)
            if d is None:
                return
            components = d

        old = components.get(name)
        if old is None:
            return
        if value is not None and old != value:
            return

        del components[name]
        n = self._provided[provided] - 1
        if n == 0:
            del self._provided[provided]
            if '_v_extendors' in self.__dict__:
                del self.__dict__['_v_extendors']

        self.changed()

        return


    def subscribe(self, required, provided, value):
        required = tuple(map(_convert_None_to_Interface, required))
        name = u''
        order = len(required)
        byorder = self._subscribers
        while len(byorder) <= order:
            byorder.append({})
        components = byorder[order]
        key = required + (provided,)
        
        for k in key:
            d = components.get(k)
            if d is None:
                d = {}
                components[k] = d
            components = d

        components[name] = components.get(name, ()) + (value, )

        if provided is not None:
            n = self._provided.get(provided, 0) + 1
            self._provided[provided] = n
            if n == 1 and '_v_extendors' in self.__dict__:
                del self.__dict__['_v_extendors']

        self.changed()

    def unsubscribe(self, required, provided, value):
        required = tuple(map(_convert_None_to_Interface, required))
        order = len(required)
        byorder = self._subscribers
        if order >= len(byorder):
            return False
        components = byorder[order]
        key = required + (provided,)
        
        for k in key:
            d = components.get(k)
            if d is None:
                return
            components = d

        components[u''] = tuple([
            v for v in components.get(u'', ())
            if v != value
            ])

        if provided is not None:
            n = self._provided[provided] - 1
            if n == 0:
                del self._provided[provided]
                if '_v_extendors' in self.__dict__:
                    del self.__dict__['_v_extendors']

        self.changed()

        return

    # XXX hack to fake out twisted's use of a private api.  We'll need
    # to add a public api to mean twisted's needs and get them to use
    # it.
    def get(self, _):
        class XXXTwistedFakeOut:
            selfImplied = {}
        return XXXTwistedFakeOut




_not_in_mapping = object()
class AdapterLookup(object):

    def __init__(self, registry):
        self._registry = registry
        self._cache = {}
        self._mcache = {}
        self._scache = {}
        self._required = {}

    def changed(self):
        self._cache.clear()
        self._mcache.clear()
        self._scache.clear()
        for r in self._required.keys():
            r = r()
            if r is not None:
                r.unsubscribe(self)
        self._required.clear()
        
    def _getcache(self, provided, name):
        cache = self._cache.get(provided)
        if cache is None:
            cache = {}
            self._cache[provided] = cache
        if name:
            c = cache.get(name)
            if c is None:
                c = {}
                cache[name] = c
            cache = c
        return cache

    def _subscribe(self, *required):
        _refs = self._required
        for r in required:
            ref = r.weakref()
            if ref not in _refs:
                r.subscribe(self)
                _refs[ref] = 1

    def lookup(self, required, provided, name=u'', default=None):
        cache = self._getcache(provided, name)
        if len(required) == 1:
            result = cache.get(required[0], _not_in_mapping)
        else:
            result = cache.get(tuple(required), _not_in_mapping)

        if result is _not_in_mapping:
            result = None
            order = len(required)
            for registry in self._registry.ro:
                byorder = registry._adapters
                if order >= len(byorder):
                    continue

                extendors = registry._v_extendors.get(provided)
                if not extendors:
                    continue

                components = byorder[order]
                result = _lookup(components, required, extendors, name, 0,
                                 order)
                if result is not None:
                    break

            self._subscribe(*required)
            if len(required) == 1:
                cache[required[0]] = result
            else:
                cache[tuple(required)] = result

        if result is None:
            return default

        return result

    def queryMultiAdapter(self, objects, provided, name=u'', default=None):
        factory = self.lookup(map(providedBy, objects), provided, name)
        if factory is None:
            return default

        result = factory(*objects)
        if result is None:
            return default

        return result        
    
    def lookup1(self, required, provided, name=u'', default=None):
        return self.lookup((required, ), provided, name, default)
    
    def queryAdapter(self, object, provided, name=u'', default=None):
        return self.adapter_hook(provided, object, name, default)

    def adapter_hook(self, provided, object, name=u'', default=None):
        factory = self.lookup1(providedBy(object), provided, name)
        if factory is not None:
            result = factory(object)
            if result is not None:
                return result

        return default

    def lookupAll(self, required, provided):
        cache = self._mcache.get(provided)
        if cache is None:
            cache = {}
            self._mcache[provided] = cache

        required = tuple(required)
        result = cache.get(required, _not_in_mapping)
        if result is _not_in_mapping:
            order = len(required)
            result = {}
            for registry in reversed(self._registry.ro):
                byorder = registry._adapters
                if order >= len(byorder):
                    continue
                extendors = registry._v_extendors.get(provided)
                if not extendors:
                    continue
                components = byorder[order]
                _lookupAll(components, required, extendors, result, 0, order)

            self._subscribe(*required)
            cache[required] = result

        return result.iteritems()

    def names(self, required, provided):
        return [c[0] for c in self.lookupAll(required, provided)]

    def subscriptions(self, required, provided):
        cache = self._scache.get(provided)
        if cache is None:
            cache = {}
            self._scache[provided] = cache

        required = tuple(required)
        result = cache.get(required, _not_in_mapping)
        if result is _not_in_mapping:
            order = len(required)
            result = []
            for registry in reversed(self._registry.ro):
                byorder = registry._subscribers
                if order >= len(byorder):
                    continue

                if provided is None:
                    extendors = (provided, )
                else:
                    extendors = registry._v_extendors.get(provided)
                    if extendors is None:
                        continue

                _subscriptions(byorder[order], required, extendors, u'',
                               result, 0, order)

        return result

    def subscribers(self, objects, provided):
        subscriptions = self.subscriptions(map(providedBy, objects), provided)
        if provided is None:
            result = ()
            for subscription in subscriptions:
                subscription(*objects)
        else:
            result = []
            for subscription in subscriptions:
                subscriber = subscription(*objects)
                if subscriber is not None:
                    result.append(subscriber)
        return result
    
def _convert_None_to_Interface(x):
    if x is None:
        return Interface
    else:
        return x

def _normalize_name(name):
    if isinstance(name, basestring):
        return unicode(name)

    raise TypeError("name must be a regular or unicode string")

def _lookup(components, specs, provided, name, i, l):
    if i < l:
        for spec in specs[i].__sro__:
            comps = components.get(spec)
            if comps:
                r = _lookup(comps, specs, provided, name, i+1, l)
                if r is not None:
                    return r
    else:
        for iface in provided:
            comps = components.get(iface)
            if comps:
                r = comps.get(name)
                if r is not None:
                    return r
                
    return None

def _lookupAll(components, specs, provided, result, i, l):
    if i < l:
        for spec in reversed(specs[i].__sro__):
            comps = components.get(spec)
            if comps:
                _lookupAll(comps, specs, provided, result, i+1, l)
    else:
        for iface in reversed(provided):
            comps = components.get(iface)
            if comps:
                result.update(comps)

def _subscriptions(components, specs, provided, name, result, i, l):
    if i < l:
        for spec in reversed(specs[i].__sro__):
            comps = components.get(spec)
            if comps:
                _subscriptions(comps, specs, provided, name, result, i+1, l)
    else:
        for iface in reversed(provided):
            comps = components.get(iface)
            if comps:
                comps = comps.get(name)
                if comps:
                    result.extend(comps)
