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

class readproperty(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, inst, class_):
        if inst is None:
            return self

        func = self.func
        return func(inst)
    

_marker = object
class AdapterRegistry(object):

    def __init__(self, bases=()):
        self._adapters = []
        self._provided = {}
        self._unnamed_subscriptions = []
        self._named_subscriptions = {}
        self.__bases__ = bases

    @apply
    def __bases__():
        def get(self):
            return self.__dict__['__bases__']
        def set(self, v):
            self.__dict__['__bases__'] = v
            self.ro = ro.ro(self)
            
        return property(get, set)


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

        return

    def lookup(self, required, provided, name=u'', default=None):
        order = len(required)
        for self in self.ro:
            byorder = self._adapters
            if order >= len(byorder):
                continue

            extendors = self._v_extendors.get(provided)
            if not extendors:
                continue
            
            components = byorder[order]
            result = _lookup(components, required, extendors, name, 0, order)
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
        order = len(required)
        result = {}
        for self in reversed(self.ro):
            byorder = self._adapters
            if order >= len(byorder):
                continue
            extendors = self._v_extendors.get(provided)
            if not extendors:
                continue
            components = byorder[order]
            _lookupAll(components, required, extendors, result, 0, order)

        return result.iteritems()

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

    # XXX hack to fake out twisted's use of a private api.  We'll need
    # to add a public api to mean twisted's needs and get them to use
    # it.
    def get(self, _):
        class XXXTwistedFakeOut:
            selfImplied = {}
        return XXXTwistedFakeOut
    
def _convert_None_to_Interface(x):
    if x is None:
        return Interface
    else:
        return x

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
                # XXX where is changed?  Where is unsubscribe on unregister?
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
                r = _lookupAll(comps, specs, provided, result, i+1, l)
                if r is not None:
                    return r
    else:
        for iface in reversed(provided):
            comps = components.get(iface)
            if comps:
                result.update(comps)





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
