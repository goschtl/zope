##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Surrogate-specification registry implementation

$Id: surrogate.py,v 1.2 2003/11/21 17:11:46 jim Exp $
"""

# Implementation notes

# We keep a collection of surrogates.

# A surrogate is a surrogate for a specification (interface or
# declaration).  We use week references in order to remove surrogates
# if the corresponding specification goes away.

# Each surrogate keeps track of:

# - The adapters registered directly for that surrogate, and

# - The "implied" adapters, which is the adapters that can be computed
#   from instances of that surrogate.

# The later data structure takes into account adapters registered for
# specifications that the registered surrogate extends.

# The registrations are of the form:

#   {(with, name, specification) -> factories}

# where:

#   with is a tuple of specs that is non-empty only in the case
#   of multi-adapters.  

#   name is a unicode adapter name.  Unnamed adapters have an empty
#   name.

#   specification is the interface being adapted to.

#   factories is normally a tuple of factories, but can be anything.
#   (See the "raw" option to the query-adapter calls.)

# The implied adapters are held in a single dictionary. The items in the
# dictionary are of 3 forms:

#   specification -> factories

#      for simple unnamed adapters

#   (specification, name) -> factories

#      for named adapters

#   (specification, name, order) -> {with -> factories}

#      for multi-adapters.  


from __future__ import generators
import weakref
from zope.interface.ro import ro
from zope.interface.declarations import providedBy
from zope.interface.interface import InterfaceClass

Default = InterfaceClass("Default", (), {})

class ReadProperty(object):

    def __init__(self, func):
        self.func = func

    def __get__(self, inst, class_):
        if inst is None:
            return self
        return self.func(inst)

class Surrogate(object):
    """Specification surrogate

    A specification surrogate is used to hold adapter registrations on
    behalf of a specification.
    """

    def __init__(self, spec, registry):
        self.spec = spec.weakref()
        spec.subscribe(self)
        self.adapters = {}
        self.dependents = weakref.WeakKeyDictionary()

        self.__bases__ = [registry.get(base) for base in spec.__bases__]
        for base in self.__bases__:
            base.subscribe(self)

    def dirty(self):
        if 'get' in self.__dict__:
            # Not already dirty
            del self.selfImplied
            del self.multImplied
            del self.get
        for dependent in self.dependents.keys():
            dependent.dirty()

    def clean(self):
        self.selfImplied, self.multImplied = adapterImplied(self.adapters)

        implied = {}

        ancestors = ro(self)

        # Collect implied data in reverse order to have more specific data
        # override less-specific data.
        ancestors.reverse()
        for ancestor in ancestors:
            implied.update(ancestor.selfImplied)
            for k, ancestor_adapters in ancestor.multImplied.iteritems():
                implied_adapters = implied.get(k)
                if implied_adapters:
                    implied_adapters.update(ancestor_adapters)
                else:
                    implied[k] = ancestor_adapters.copy()

        self.get = implied.get

    def get(self, key):
        """Get an implied value

        This is only called when the surrogate is dirty
        """
        self.clean()
        return self.__dict__['get'](key)

    def selfImplied(self):
        """Return selfImplied when dirty
        """
        self.clean()
        return self.__dict__['selfImplied']
    selfImplied = ReadProperty(selfImplied)

    def multiImplied(self):
        """Return _multiImplied when dirty
        """
        self.clean()
        return self.__dict__['multiImplied']
    multiImplied = ReadProperty(multiImplied)

    def subscribe(self, dependent):
        self.dependents[dependent] = 1

    def unsubscribe(self, dependent):
        del self.dependents[dependent]

    def _adaptTo(self, specification, factories, name='', with=()):
        if factories is None:
            try:
                del self.adapters[with, name, specification]
            except KeyError:
                pass
        else:
            self.adapters[tuple(with), name, specification] = factories

        self.dirty()

    def changed(self, which=None):
        self.dirty()

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self.spec())

class SurrogateRegistry(object):
    """Surrogate registry
    """

    # Implementation node:
    # We are like a weakref dict ourselves. We can't use a weakref
    # dict because we have to use spec.weakref() rather than
    # weakref.ref(spec) to get weak refs to specs.

    _surrogateClass = Surrogate

    def __init__(self):
        default = self._surrogateClass(Default, self)
        self._default = default
        surrogates = {Default.weakref(): default}
        self._surrogates = surrogates

        def _remove(k):
            try:
                del surrogates[k]
            except KeyError:
                pass

        self._remove = _remove

    def get(self, declaration):
        if declaration is None:
            return self._default

        ref = declaration.weakref(self._remove)
        surrogate = self._surrogates.get(ref)
        if surrogate is None:
            surrogate = self._surrogateClass(declaration, self)
            self._surrogates[ref] = surrogate

        return surrogate


    def provideAdapter(self, required, provided, factories, name=u'', with=()):
        """Register an adapter

        Note that the given name must be convertable to unicode.
        Use an empty string for unnamed adapters. It is impossible to
        have a named adapter with an empty name.
        """
        required = self.get(required)
        if with:
            with = tuple(with)
        else:
            with = ()

        if not isinstance(name, basestring):
            raise TypeError("The name provided to provideAdapter "
                            "must be a string or unicode")
        required._adaptTo(provided, factories, unicode(name), with)

    def queryAdapter(self, ob, interface, default=None, raw=False):
        """Query a simple adapter

           >>> import zope.interface
           >>> class F0(zope.interface.Interface):
           ...     pass
           >>> class F1(F0):
           ...     pass

           >>> class C:
           ...     zope.interface.implements(F1)
           >>> c = C()

           >>> registry = SurrogateRegistry()

           Adapting to some other interface for which there is no
           adapter returns the default:

           >>> class B0(zope.interface.Interface):
           ...     pass
           >>> class B1(B0):
           ...     pass

           >>> registry.queryAdapter(c, B0)
           >>> registry.queryAdapter(c, B0, 42)
           42

           Unless we define an adapter:

           >>> def f1(ob):
           ...     return 1

           >>> registry.provideAdapter(F0, B1, [f1])
           >>> registry.queryAdapter(c, B0)
           1

           If we define a more specific adapter (for F1), we'll get that:

           >>> def f2(ob):
           ...     return 2

           >>> registry.provideAdapter(F1, B1, [f2])
           >>> registry.queryAdapter(c, B0)
           2

           >>> def f3(ob):
           ...     return 3

           >>> registry.provideAdapter(F1, B0, [f3])
           >>> registry.queryAdapter(c, B0)
           3
           """

        declaration = providedBy(ob)
        s = self.get(declaration)

        factories = s.get(interface)
        if factories is None:
            factories = self._default.get(interface)

        if factories is not None:
            if raw:
                return factories
            
            for factory in factories:
                ob = factory(ob)
            return ob

        return default

    def queryNamedAdapter(self, ob, interface, name, default=None, raw=False):
        """Query a named simple adapter

        >>> import zope.interface
        >>> class F0(zope.interface.Interface):
        ...     pass
        >>> class F1(F0):
        ...     pass

        >>> class C:
        ...     zope.interface.implements(F1)
        >>> c = C()

        >>> registry = SurrogateRegistry()

        If we ask for a named adapter, we won't get a result unless there
        is a named adapter, even if the object implements the interface:

        >>> registry.queryNamedAdapter(c, F0, 'bob')
            
        >>> class B0(zope.interface.Interface):
        ...     pass
        >>> class B1(B0):
        ...     pass


        >>> def f1(ob):
        ...     return 1

        >>> registry.provideAdapter(F0, B1, [f1], name='bob')
        >>> registry.queryNamedAdapter(c, B0, 'bob')
        1
        >>> registry.queryNamedAdapter(c, B0, 'bruce')
        

        >>> def f2(ob):
        ...     return 2

        >>> registry.provideAdapter(F1, B1, [f2], name='bob')
        >>> registry.queryNamedAdapter(c, B0, 'bob')
        2
        
        >>> def f3(ob):
        ...     return 3

        >>> registry.provideAdapter(F1, B0, [f3], name='bob')
        >>> registry.queryNamedAdapter(c, B0, 'bob')
        3

        """

        declaration = providedBy(ob)
        s = self.get(declaration)
        key = name and (interface, name) or interface
        factories = s.get(key)
        if factories is None:
            factories = self._default.get(key)
        if factories is not None:
            if raw:
                return factories
            for factory in factories:
                ob = factory(ob)
            return ob

        return default

    def queryMultiAdapter(self, objects, interface, name=u'',
                          default=None, raw=False):
        """

        >>> import zope.interface
        >>> class IF0(zope.interface.Interface):
        ...     pass
        >>> class IF1(IF0):
        ...     pass

        >>> class IR0(zope.interface.Interface):
        ...     pass
        >>> class IR1(IR0):
        ...     pass

        >>> class F1:
        ...     zope.interface.implements(IF1)
        >>> c = F1()

        >>> class R1:
        ...     zope.interface.implements(IR1)
        >>> r = R1()

        >>> registry = SurrogateRegistry()

        If we ask for a multi adapter, we won't get a result unless there
        is a named adapter, even if the object implements the interface:

        >>> registry.queryMultiAdapter((c, r), IF0, 'bob')

        >>> class IB0(zope.interface.Interface):
        ...     pass
        >>> class IB1(IB0):
        ...     pass


        >>> class f1:
        ...     def __init__(self, x, y):
        ...         self.x, self.y = x, y


        >>> registry.provideAdapter(IF0, IB1, [f1], name='bob', with=[IR0])
        >>> a = registry.queryMultiAdapter((c, r), IB0, 'bob')
        >>> a.__class__ is f1
        True
        >>> a.x is c
        True
        >>> a.y is r
        True

        >>> registry.queryMultiAdapter((c, r), IB0, 'bruce')

        >>> class f2(f1):
        ...     pass

        >>> registry.provideAdapter(IF1, IB1, [f2], name='bob', with=[IR1])
        >>> a = registry.queryMultiAdapter((c, r), IB0, 'bob')
        >>> a.__class__ is f2
        True
        >>> a.x is c
        True
        >>> a.y is r
        True
        
        """
        ob = objects[0]
        order = len(objects)
        obs = objects[1:]

        declaration = providedBy(ob)
        surrogate = self.get(declaration)

        while 1:
            adapters = surrogate.get((interface, name, order))
            if adapters:
                matched = None
                matched_factories = None
                for interfaces, factories in adapters.iteritems():
                    for iface, ob in zip(interfaces, obs):
                        if not iface.isImplementedBy(ob):
                            break # This one is no good
                    else:
                        # we didn't break, so we have a match
                        if matched is None:
                            matched = interfaces
                            matched_factories = factories
                        else:
                            # see if the new match is better than the old one:
                            for iface, m in zip(interfaces, matched):
                                if iface.extends(m):
                                    # new is better than old
                                    matched = interfaces
                                    matched_factories = factories
                                    break
                                elif m.extends(iface):
                                    # old is better than new
                                    break
                                

                if matched_factories is not None:
                    if raw:
                        return matched_factories

                    assert len(matched_factories) == 1

                    return matched_factories[0](*objects)

            # Fall back to default if we haven't already
            if surrogate is self._default:
                return default
            surrogate = self._default

    def getRegisteredMatching(self,
                              required=None,
                              provided=None,
                              name=None,
                              with=None,
                              ):
        """Search for registered adapters

           Return a 5-tuple with:

           - (first) required interface

           - provided interface

           - a tuple of additional required interfaces (for multi-adapters)

           - name, and

           - a sequence of factories. (Note that this could be arbitrary data).
           

           Note, this is usually slow!

           >>> from zope.interface import Interface

           >>> class R1(Interface):
           ...     pass
           >>> class R12(Interface):
           ...     pass
           >>> class R2(R1):
           ...     pass
           >>> class R3(R2):
           ...     pass
           >>> class R4(R3):
           ...     pass

           >>> class P1(Interface):
           ...     pass
           >>> class P2(P1):
           ...     pass
           >>> class P3(P2):
           ...     pass
           >>> class P4(P3):
           ...     pass


           >>> registry = SurrogateRegistry()
           >>> registry.provideAdapter(None, P3, 'default P3')
           >>> registry.provideAdapter(Interface, P3, 'any P3')
           >>> registry.provideAdapter(R2, P3, 'R2 P3')
           >>> registry.provideAdapter(R2, P3, "bobs R2 P3", name='bob')

           >>> from pprint import PrettyPrinter
           >>> pprint = PrettyPrinter(width=60).pprint
           >>> def sorted(x):
           ...    x = [(getattr(r, '__name__', None), p.__name__, w, n, f)
           ...         for (r, p, w, n, f) in x]
           ...    x.sort()
           ...    pprint(x)

           >>> sorted(registry.getRegisteredMatching())
           [(None, 'P3', (), u'', 'default P3'),
            ('Interface', 'P3', (), u'', 'any P3'),
            ('R2', 'P3', (), u'', 'R2 P3'),
            ('R2', 'P3', (), u'bob', 'bobs R2 P3')]

           >>> sorted(registry.getRegisteredMatching(name=''))
           [(None, 'P3', (), u'', 'default P3'),
            ('Interface', 'P3', (), u'', 'any P3'),
            ('R2', 'P3', (), u'', 'R2 P3')]

           >>> sorted(registry.getRegisteredMatching(required=[R1]))
           [(None, 'P3', (), u'', 'default P3'),
            ('Interface', 'P3', (), u'', 'any P3')]

           >>> sorted(registry.getRegisteredMatching(required=R1))
           [(None, 'P3', (), u'', 'default P3'),
            ('Interface', 'P3', (), u'', 'any P3')]

           >>> sorted(registry.getRegisteredMatching(provided=[P1]))
           [(None, 'P3', (), u'', 'default P3'),
            ('Interface', 'P3', (), u'', 'any P3'),
            ('R2', 'P3', (), u'', 'R2 P3'),
            ('R2', 'P3', (), u'bob', 'bobs R2 P3')]

           >>> sorted(registry.getRegisteredMatching(provided=P1))
           [(None, 'P3', (), u'', 'default P3'),
            ('Interface', 'P3', (), u'', 'any P3'),
            ('R2', 'P3', (), u'', 'R2 P3'),
            ('R2', 'P3', (), u'bob', 'bobs R2 P3')]

           >>> sorted(registry.getRegisteredMatching(provided=P3))
           [(None, 'P3', (), u'', 'default P3'),
            ('Interface', 'P3', (), u'', 'any P3'),
            ('R2', 'P3', (), u'', 'R2 P3'),
            ('R2', 'P3', (), u'bob', 'bobs R2 P3')]

           >>> sorted(registry.getRegisteredMatching(
           ...     required = (R4, R12),
           ...     provided = (P1, )))
           [(None, 'P3', (), u'', 'default P3'),
            ('Interface', 'P3', (), u'', 'any P3'),
            ('R2', 'P3', (), u'', 'R2 P3'),
            ('R2', 'P3', (), u'bob', 'bobs R2 P3')]

           >>> sorted(registry.getRegisteredMatching(
           ...     required = (R4, R12),
           ...     provided = (P3, )))
           [(None, 'P3', (), u'', 'default P3'),
            ('Interface', 'P3', (), u'', 'any P3'),
            ('R2', 'P3', (), u'', 'R2 P3'),
            ('R2', 'P3', (), u'bob', 'bobs R2 P3')]

           >>> sorted(registry.getRegisteredMatching(
           ...     required = (R2, ),
           ...     provided = (P3, )))
           [(None, 'P3', (), u'', 'default P3'),
            ('Interface', 'P3', (), u'', 'any P3'),
            ('R2', 'P3', (), u'', 'R2 P3'),
            ('R2', 'P3', (), u'bob', 'bobs R2 P3')]

           >>> sorted(registry.getRegisteredMatching(
           ...     required = (R2, ),
           ...     provided = (P3, ),
           ...     name='bob'))
           [('R2', 'P3', (), u'bob', 'bobs R2 P3')]

           >>> sorted(registry.getRegisteredMatching(
           ...     required = (R3, ),
           ...     provided = (P1, ),
           ...     name='bob'))
           [('R2', 'P3', (), u'bob', 'bobs R2 P3')]

           """

        if name is not None:
            name = unicode(name)
        
        if isinstance(required, InterfaceClass):
            required = (required, )
        elif required is None:
            required = [ref() for ref in self._surrogates.keys()
                                   if ref() is not None]

        required = tuple(required)+(None,)

        if isinstance(provided, InterfaceClass):
            provided = (provided, )


        seen = {}

        for required in required:
            s = self.get(required)
            for ancestor in ro(s):
                if ancestor in seen:
                    continue
                seen[ancestor] = 1
                adapters = ancestor.adapters
                if adapters:
                    items = adapters.iteritems()
                    ancestor = ancestor.spec()
                    if ancestor is Default:
                        ancestor = None
                    for (rwith, aname, target), factories in items:
                        if with is not None and not mextends(with, rwith):
                            continue
                        if name is not None and aname != name:
                            continue

                        if provided:
                            for p in provided:
                                if target.extends(p, False):
                                    break
                            else:
                                # None matching
                                continue

                        yield (ancestor, target, rwith, aname, factories)

def mextends(with, rwith):
    if len(with) == len(rwith):
        for w, r in zip(with, rwith):
            if not w.isOrExtends(r):
                break
        else:
            return True
    return False
        

def adapterImplied(adapters):
    implied = {}
    multi = {}
    registered = {}

    # Add adapters and interfaces directly implied by same:
    for (with, name, target), factories in adapters.iteritems():
        if with:
            _add_multi_adapter(with, name, target, target, multi,
                               registered, factories)
        elif name:
            _add_named_adapter(target, target, name, implied,
                               registered, factories)
        else:
            _add_adapter(target, target, implied, registered, factories)

    return implied, multi

def _add_adapter(target, provided, implied, registered, factories):
    if (target not in implied
        or
        (target in registered and registered[target].extends(provided))
        ):
        registered[target] = provided
        implied[target] = factories
        for b in target.__bases__:
            _add_adapter(b, provided, implied, registered, factories)

def _add_named_adapter(target, provided, name,
                        implied, registered, factories):
    key = target, name
    if (key not in implied
        or
        (key in registered and registered[key].extends(provided))
        ):
        registered[key] = provided
        implied[key] = factories
        for b in target.__bases__:
            _add_named_adapter(b, provided, name,
                               implied, registered, factories)

def _add_multi_adapter(interfaces, name, target, provided, implied,
                       registered, factories):
    order = len(interfaces)+1
    key = target, name, order
    adapters = implied.get(key)
    if adapters is None:
        adapters = {}
        implied[key] = adapters

    key = key, interfaces # The full key has all 4
    if key not in registered or registered[key].extends(provided):
        # This is either a new entry or it is an entry for a more
        # general interface that is closer provided than what we had
        # before
        registered[key] = provided
        adapters[interfaces] = factories

    for b in target.__bases__:
        _add_multi_adapter(interfaces, name, b, provided, implied,
                           registered, factories)
