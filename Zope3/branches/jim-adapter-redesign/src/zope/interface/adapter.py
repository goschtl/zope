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

from zope.interface import providedBy, Interface, ro

_marker = object
class AdapterRegistry(object):

    def __init__(self, bases=()):
        self._unnamed_adapters = [] # [{ provided -> components }]
        self._named_adapters = {} # { name -> [{ provided -> components }] }
        self._unnamed_subscriptions = [] # ditto
        self._named_subscriptions = {} # ditto
        self.__bases__ = bases

    def __bases__():
        def get(self):
            return self.__dict__['__bases__']
        def set(self, v):
            self.__dict__['__bases__'] = v
            self.ro = ro.ro(self)
            
        return property(get, set)
    __bases__ = __bases__()
        
    def register(self, required, provided, name, value):
        if value is None:
            self.unregister(required, provided, name, value)
            return

        if name:
            name = _normalize_name(name)
            byorder = self._named_adapters.get(name)
            if byorder is None:
                self._named_adapters[name] = byorder = []
        else:
            byorder = self._unnamed_adapters

        order = len(required)
        while len(byorder) <= order:
            byorder.append(Adapters())

        components = byorder[order]
        components.register(required, provided, value)
        
    def unregister(self, required, provided, name, value=None):
        if name:
            name = _normalize_name(name)
            byorder = self._named_adapters.get(name)
            if byorder is None:
                return
        else:
            byorder = self._unnamed_adapters

        order = len(required)
        if order >= len(byorder):
            return
        components = byorder[order]
        components.unregister(required, provided, value)


    def lookup(self, required, provided, name=u'', default=None):
        for self in self.ro:
            if name:
                byorder = self._named_adapters.get(name)
                if byorder is None:
                    continue
            else:
                byorder = self._unnamed_adapters

            order = len(required)
            if order >= len(byorder):
                continue

            components = byorder[order]
            result = lookup(components.components, required, provided)
            if result is not None:
                return result

        return default

    def queryMultiAdapter(self, objects, provided, name=u'', default=None):
        factory = self.lookup(map(providedBy, objects), provided, name)
        if factory is None:
            return default

        result = factory(*objects)
        if result is None:
            return default

        return result        

    def lookup1(self, required, provided, name=u'', default=None):
        for self in self.ro:
            if name:
                byorder = self._named_adapters.get(name)
                if byorder is None:
                    continue
            else:
                byorder = self._unnamed_adapters

            if 1 >= len(byorder):
                continue

            components = byorder[1]
            result = lookup1(components.components, required, provided)
            if result is not None:
                return result

        return default

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
        for self in self.ro:
            order = len(required)
            if order < len(self._unnamed_adapters):
                result = lookup(self._unnamed_adapters[order].components,
                                required, provided)
                if result is not None:
                    yield (u'', result)

            for name, byorder in self._named_adapters.iteritems():
                if order < len(byorder):
                    result = lookup(byorder[order].components,
                                    required, provided)
                    if result is not None:
                        yield (name, result)

    def names(self, required, provided):
        return [c[0] for c in self.lookupAll(required, provided)]

    def subscribe(self, required, provided, value):

# XXX when we are ready to support named subscribers, we'll add a name
# argument and uncomment the following.
##         if name:
##             name = _normalize_name(name)
##             byorder = self._named_subscriptions.get(name)
##             if byorder is None:
##                 self._named_subscriptions[name] = byorder = []
##         else:
##             byorder = self._unnamed_subscriptions

        byorder = self._unnamed_subscriptions

        order = len(required)
        while len(byorder) <= order:
            byorder.append(Subscriptions())

        components = byorder[order]
        components.register(required, provided, value)

    def unsubscribe(self, required, provided, value):

# XXX when we are ready to support named subscribers, we'll add a name
# argument and uncomment the following.
##         if name:
##             name = _normalize_name(name)
##             byorder = self._named_subscriptions.get(name)
##             if byorder is None:
##                 self._named_subscriptions[name] = byorder = []
##         else:
##             byorder = self._unnamed_subscriptions

        byorder = self._unnamed_subscriptions

        order = len(required)
        if len(byorder) <= order:
            return

        components = byorder[order]
        components.unregister(required, provided, value)

    def subscriptions(self, required, provided, name=u''):
        result = []
        # XXX should we traverse ro in reverse?
        for self in self.ro:
            if name:
                byorder = self._named_subscriptions.get(name)
                if byorder is None:
                    continue
            else:
                byorder = self._unnamed_subscriptions

            order = len(required)
            if order >= len(byorder):
                continue
            
            subscriptions(byorder[order].components, required, provided,
                          result)

        return result

    def subscribers(self, objects, provided, name=u''):
        if provided is None:
            result = ()
        else:
            result = []
            
        for self in self.ro:
            if name:
                byorder = self._named_subscriptions.get(name)
                if byorder is None:
                    continue
            else:
                byorder = self._unnamed_subscriptions

            order = len(objects)
            if order >= len(byorder):
                continue

            subscribers(byorder[order].components, objects, provided, result)

        return result

def _normalize_name(name):
    if isinstance(name, basestring):
        return unicode(name)

    raise TypeError("name must be a regular or unicode string")

        
class Next:

    def __init__(self, spec, basis):
        sro = spec.__sro__
        self.__sro__ = sro[sro.index(basis)+1:]
        

class Adapters(object):

    def __init__(self):
        self.components = {}
        self.provided = {} # {iface -> (iro, [(required, value)])}

    def register(self, required, provided, value):
        if (provided is None) or (provided is Interface):
            self._register(required, provided, provided, value)
        else:
            registered = self.provided.get(provided)
            if registered is None:
                self.provided[provided] = registered = provided.__iro__, []
                provided.subscribe(self)
            registered[1].append((required, value))

            for p in provided.__iro__:
                self._register(required, provided, p, value)

    def _register(self, required, provided, p, value):
        d = self.components
        k = p
        for r in required:
            if r is None:
                r = Interface
            v = d.get(k)
            if v is None:
                d[k] = v = {}
            d = v
            k = r

        components = d.get(k, ())
        d[k] = self._add(components, provided, value)

    def _add(self, components, provided, value):
        if provided is None:
            return components + ((value, provided), )
        
        return (
            tuple([c for c in components if provided.extends(c[1])])
            +
            ((value, provided), )
            +
            tuple([c for c in components if not provided.extends(c[1])])
            )
        
    def unregister(self, required, provided, value):
        if (provided is None) or (provided is Interface):
            self._unregister(required, provided, provided, value)
        else:
            registered = self.provided.get(provided)
            if registered is None:
                return
            if value is None:
                rv = [r for r in registered[1] if r[0] != required]
            else:
                rv = [r for r in registered[1] if r != (required, value)]

            if rv:
                self.provided[provided] = registered[0], rv
            else:
                del self.provided[provided]

            for p in provided.__iro__:
                self._unregister(required, provided, p, value)

    def _unregister(self, required, provided, p, value):
        items = []
        d = self.components
        k = p
        for r in required:
            if r is None:
                r = Interface
            v = d.get(k)
            if v is None:
                return
            items.append((d, k))
            d = v
            k = r

        components = d.get(k, None)
        if components is None:
            return

        if value is None:
            # unregister all
            components = [c for c in components
                          if c[1] != provided]
        else:
            # unregister just this one
            components = [c for c in components
                          if c != (value, provided)]

        if components:
            d[k] = tuple(components)
        else:
            del d[k]

            items.reverse()
            for d, k in items:
                if not d[k]:
                    del d[k]

class Subscriptions(Adapters):

    def _add(self, components, provided, value):
        return components + ((value, provided), )

def _lookup(components, specs, i, l):
    if i < l:
        for spec in specs[i].__sro__:
            comps = components.get(spec)
            if comps is not None:
                r = _lookup(comps, specs, i+1, l)
                if r is not None:
                    return r
        return None
    
    return components

def lookup(components, required, provided):
    components = components.get(provided)
    if components:

        if required:
            components = _lookup(components, required, 0, len(required))
            if not components:
                return None

        return components[0][0]

    return None

def lookup1(components, required, provided):
    components = components.get(provided)
    if components:
        for s in required.__sro__:
            comps = components.get(s)
            if comps:
                return comps[0][0]

    return None

def _subscribers(components, specs, i, l, objects, result):
    if i < l:
        sro = list(specs[i].__sro__)
        sro.reverse()
        for spec in sro:
            comps = components.get(spec)
            if comps is not None:
                _subscribers(comps, specs, i+1, l, objects, result)
    else:
        if objects is None:
            result.extend([c[0] for c in components])
        else:
            for c in components:
                c = c[0](*objects)
                if c is not None and result is not None:
                    result.append(c)

def subscriptions(components, required, provided, result):
    components = components.get(provided)
    if components:
        _subscribers(components, required, 0, len(required), None, result)

def subscribers(components, objects, provided, result):
    components = components.get(provided)
    if components:
        required = map(providedBy, objects)

        if provided is None:
            result == None

        _subscribers(components, required, 0, len(required), objects, result)

try:
    from _zope_interface_coptimizations import lookup, lookup1
    from _zope_interface_coptimizations import subscribers, subscriptions
except ImportError:
    pass
    
