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

$Id: surrogate.py,v 1.4 2004/02/09 08:20:11 jim Exp $
"""

# Implementation notes

# We keep a collection of surrogates.

# A surrogate is a surrogate for a specification (interface or
# declaration).  We use weak references in order to remove surrogates
# if the corresponding specification goes away.

# Each surrogate keeps track of:

# - The adapters registered directly for that surrogate, and

# - The "implied" adapters, which is the adapters that can be computed
#   from instances of that surrogate.

# The later data structure takes into account adapters registered for
# specifications that the registered surrogate extends.

# The registrations are of the form:

#   {(subscription, with, name, specification) -> factories}

# where:

#   'subscription' is a flag indicating if this registration is for
#   subscription adapters.

#   'with' is a tuple of specs that is non-empty only in the case
#   of multi-adapters.  

#   'name' is a unicode adapter name.  Unnamed adapters have an empty
#   name.

#   'specification' is the interface being adapted to.

#   'factories' is normally a tuple of factories, but can be anything.
#   (See the "raw" option to the query-adapter calls.)  For subscription
#   adapters, it is a tuple of tuples of factories.

# The implied adapters are held in a single dictionary. The items in the
# dictionary are of 3 forms:

#   (subscription, specification) -> factories

#      for simple unnamed adapters

#   (subscription, specification, name) -> factories

#      for named adapters

#   (subscription, specification, name, order) -> {with -> factories}

#      for multi-adapters.  


from __future__ import generators
import weakref
from sets import Set
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
            for key, adapters in ancestor.selfImplied.iteritems():
                subscription = key[0]
                if subscription:
                    adapters = tuple(map(tuple, adapters))
                    implied[key] = tuple(Set(implied.get(key, ()) + adapters))
                else:
                    implied[key] = adapters
            for k, ancestor_adapters in ancestor.multImplied.iteritems():
                implied_adapters = implied.get(k)
                if implied_adapters:
                    subscription = k[0]
                    if subscription:
                        for key, adapters in ancestor_adapters.iteritems():
                            # XXX: remove dupes?
                            implied_adapters[key] = implied_adapters.get(
                                key, []) + adapters
                    else:
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
                del self.adapters[False, tuple(with), name, specification]
            except KeyError:
                pass
        else:
            self.adapters[False, tuple(with), name, specification] = factories

        self.dirty()

    def _subscriptionAdaptTo(self, specification, factories, name='', with=()):
        if factories is None:
            raise TypeError, ("Unregistering subscription adapters" 
                              " isn't implemented")

        # Add factories to our list of factory lists.
        key = (True, tuple(with), name, specification)
        factoriesList = self.adapters.get(key, ())
        factoriesList = factoriesList + (factories,)
        self.adapters[key] = factoriesList

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

    def provideSubscriptionAdapter(self, required, provided, factories,
                                   name=u'', with=()):
        """Register a subscription adapter

        Note that the given name must be convertable to unicode.
        Use an empty string for unnamed subscription adapters. It is
        impossible to have a named subscription adapter with an empty name.
        """
        required = self.get(required)
        if with:
            with = tuple(with)
        else:
            with = ()

        if not isinstance(name, basestring):
            raise TypeError("The name provided to provideAdapter "
                            "must be a string or unicode")
        required._subscriptionAdaptTo(provided, factories, unicode(name), with)

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

        factories = s.get((False, interface))
        if factories is None:
            factories = self._default.get((False, interface))

        if factories is not None:
            if raw:
                return factories
            
            for factory in factories:
                ob = factory(ob)
            return ob

        return default


    def querySubscriptionAdapter(self, ob, interface, name=u'', default=(),
                            raw=False):
        """Query for subscription adapters

        >>> import zope.interface
        >>> class IAnimal(zope.interface.Interface):
        ...     pass
        >>> class IPoultry(IAnimal):
        ...     pass
        >>> class IChicken(IPoultry):
        ...     pass
        >>> class ISeafood(IAnimal):
        ...     pass

        >>> class Poultry:
        ...     zope.interface.implements(IPoultry)
        >>> poultry = Poultry()

        >>> registry = SurrogateRegistry()

        Adapting to some other interface for which there is no
        subscription adapter returns the default:

        >>> class IRecipe(zope.interface.Interface):
        ...     pass
        >>> class ISausages(IRecipe):
        ...     pass
        >>> class INoodles(IRecipe):
        ...     pass
        >>> class IKFC(IRecipe):
        ...     pass

        >>> list(registry.querySubscriptionAdapter(poultry, IRecipe))
        []
        >>> registry.querySubscriptionAdapter(poultry, IRecipe, default=42)
        42

        Unless we define a subscription adapter:

        >>> def sausages(ob):
        ...     return 'sausages'

        >>> registry.provideSubscriptionAdapter(IAnimal, ISausages, [sausages])
        >>> list(registry.querySubscriptionAdapter(poultry, ISausages))
        ['sausages']

        And define another subscription adapter:

        >>> def noodles(ob):
        ...     return 'noodles'

        >>> registry.provideSubscriptionAdapter(IPoultry, INoodles, [noodles])
        >>> meals = list(registry.querySubscriptionAdapter(poultry, IRecipe))
        >>> meals.sort()
        >>> meals
        ['noodles', 'sausages']

        >>> class Chicken:
        ...     zope.interface.implements(IChicken)
        >>> chicken = Chicken()

        >>> def kfc(ob):
        ...     return 'kfc'

        >>> registry.provideSubscriptionAdapter(IChicken, IKFC, [kfc])
        >>> meals = list(registry.querySubscriptionAdapter(chicken, IRecipe))
        >>> meals.sort()
        >>> meals
        ['kfc', 'noodles', 'sausages']

        And the answer for poultry hasn't changed:

        >>> registry.provideSubscriptionAdapter(IPoultry, INoodles, [noodles])
        >>> meals = list(registry.querySubscriptionAdapter(poultry, IRecipe))
        >>> meals.sort()
        >>> meals
        ['noodles', 'sausages']
        """

        declaration = providedBy(ob)
        s = self.get(declaration)

        if name:
            key = (True, interface, name)
        else:
            key = (True, interface)

        factoriesLists = s.get(key)
        if factoriesLists is None:
            factoriesLists = self._default.get(key)

        if factoriesLists is not None:
            if raw:
                return factoriesLists
            
            return [factory(ob)
                    for factories in factoriesLists
                    for factory in factories]

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
        if name:
            key = (False, interface, name)
        else:
            key = (False, interface)
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
                          default=None, raw=False, _subscription=False):
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
        if _subscription:
            result = []

        surrogates = (self.get(declaration), self._default)

        for surrogate in surrogates:
            adapters = surrogate.get((_subscription, interface, name, order))
            if adapters:
                if _subscription:
                    matched_factories = []
                else:
                    matched = None
                    matched_factories = None
                for interfaces, factories in adapters.iteritems():
                    for iface, ob in zip(interfaces, obs):
                        if not iface.isImplementedBy(ob):
                            break # This one is no good
                    else:
                        if _subscription:
                            matched_factories.extend(factories)
                        else:
                            # we didn't break, so we have a match
                            if matched is None:
                                matched = interfaces
                                matched_factories = factories
                            else:
                                # see if the new match is better than the old
                                # one:
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

                    if not _subscription:
                        assert len(matched_factories) == 1, \
                               "matched_factories has more than 1 element: " \
                               + repr(matched_factories)
                        return matched_factories[0](*objects)
                    else:
                        for factories in matched_factories:
                            assert len(factories) == 1
                            result.append(factories[0](*objects))

        if _subscription and result:
            return result
        else:
            return default

    def querySubscriptionMultiAdapter(self, objects, interface, name=u'',
                                 default=(), raw=False):
        """
        Subscription multiadaption works too:

        >>> import zope.interface
        >>> class IAnimal(zope.interface.Interface):
        ...     pass
        >>> class IPoultry(IAnimal):
        ...     pass
        >>> class IChicken(IPoultry):
        ...     pass
        >>> class ISeafood(IAnimal):
        ...     pass

        >>> class Animal:
        ...     zope.interface.implements(IAnimal)
        >>> animal = Animal()

        >>> class Poultry:
        ...     zope.interface.implements(IPoultry)
        >>> poultry = Poultry()

        >>> class Poultry:
        ...     zope.interface.implements(IPoultry)
        >>> poultry = Poultry()

        >>> class Chicken:
        ...     zope.interface.implements(IChicken)
        >>> chicken = Chicken()
        

        >>> class IRecipe(zope.interface.Interface):
        ...     pass
        >>> class ISausages(IRecipe):
        ...     pass
        >>> class INoodles(IRecipe):
        ...     pass
        >>> class IKFC(IRecipe):
        ...     pass

        >>> class IDrink(zope.interface.Interface):
        ...     pass

        >>> class Drink:
        ...     zope.interface.implements(IDrink)
        >>> drink = Drink()

        >>> class Meal:
        ...     def __init__(self, animal, drink):
        ...         self.animal, self.drink = animal, drink
        >>> class Lunch(Meal):
        ...     pass
        >>> class Dinner(Meal):
        ...     pass

        >>> registry = SurrogateRegistry()
        >>> query = registry.querySubscriptionMultiAdapter
        >>> provide = registry.provideSubscriptionAdapter

        Can't find adapters for insufficiently specific interfaces:
        
        >>> provide(IPoultry, IRecipe, [Dinner], with=[IDrink])
        >>> list(query((animal, drink), IRecipe))
        []

        But we can for equally specific:

        >>> adapters = list(query((poultry, drink), IRecipe))
        >>> len(adapters)
        1

        And for more specific:

        >>> adapters = list(query((chicken, drink), IRecipe))
        >>> len(adapters)
        1

        >>> provide(IAnimal, IRecipe, [Meal], with=[IDrink])
        >>> provide(IAnimal, IRecipe, [Lunch], with=[IDrink])
        >>> adapters = list(query((animal, drink), IRecipe)) 
        >>> names = [a.__class__.__name__ for a in adapters]
        >>> names.sort()
        >>> names
        ['Lunch', 'Meal']
        >>> adapters[0].animal is animal
        True
        >>> adapters[0].drink is drink
        True
        >>> adapters[1].animal is animal
        True
        >>> adapters[1].drink is drink
        True

        Mixed specificities:

        >>> registry = SurrogateRegistry()
        >>> query = registry.querySubscriptionMultiAdapter
        >>> provide = registry.provideSubscriptionAdapter

        >>> provide(IPoultry, IRecipe, [Meal], with=[IDrink])
        >>> provide(IChicken, IRecipe, [Lunch], with=[IDrink])

        We can only use IPoultry recipes on poultry -- we can't apply chicken
        recipes because poultry isn't specific enough.  So there's only one
        choice for poultry:
        
        >>> adapters = list(query((poultry, drink), IRecipe))
        >>> len(adapters)
        1

        But using chicken, we can use poultry *and* chicken recipes:
        
        >>> adapters = list(query((chicken, drink), IRecipe))
        >>> len(adapters)
        2

        We should get the same results if we swap the order of the input types:

        >>> registry = SurrogateRegistry()
        >>> query = registry.querySubscriptionMultiAdapter
        >>> provide = registry.provideSubscriptionAdapter

        >>> provide(IDrink, IRecipe, [Meal], with=[IPoultry])
        >>> provide(IDrink, IRecipe, [Lunch], with=[IChicken])

        >>> adapters = list(query((drink,poultry), IRecipe))
        >>> len(adapters)
        1
        >>> adapters = list(query((drink,chicken), IRecipe))
        >>> len(adapters)
        2

        And check that names work, too:

        >>> adapters = list(query((drink,poultry), IRecipe, name='Joes Diner'))
        >>> len(adapters)
        0
        
        >>> provide(IDrink, IRecipe, [Meal], with=[IPoultry],name='Joes Diner')
        >>> adapters = list(query((drink,poultry), IRecipe, name='Joes Diner'))
        >>> len(adapters)
        1

        """
        return self.queryMultiAdapter(objects, interface, name, default, raw,
                                      _subscription=True)

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
                    for key, factories in items:
                        subscription, rwith, aname, target = key
                        if subscription:
                            raise NotImplementedError
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

    for key, factories in adapters.iteritems():

        # XXX Backward compatability
        # Don't need to handle 3-tuples some day
        try:
            (subscription, with, name, target) = key
        except ValueError:
            (with, name, target) = key
            subscription = False
        if with:
            _add_multi_adapter(with, name, target, target, multi,
                               registered, factories, subscription)
        elif name:
            _add_named_adapter(target, target, name, implied,
                               registered, factories, subscription)
        else:
            _add_adapter(target, target, implied, registered, factories,
                         subscription)

    return implied, multi

def _add_adapter(target, provided, implied, registered, factories,
                 subscription):
    key = subscription, target
    if (key not in implied
        or
        (key in registered and registered[key].extends(provided))
        ):
        registered[key] = provided
        implied[key] = factories
        for b in target.__bases__:
            _add_adapter(b, provided, implied, registered, factories,
                         subscription)

def _add_named_adapter(target, provided, name,
                        implied, registered, factories, subscription):
    key = subscription, target, name
    if (key not in implied
        or
        (key in registered and registered[key].extends(provided))
        ):
        registered[key] = provided
        implied[key] = factories
        for b in target.__bases__:
            _add_named_adapter(b, provided, name,
                               implied, registered, factories, subscription)

def _add_multi_adapter(interfaces, name, target, provided, implied,
                       registered, factories, subscription):
    order = len(interfaces)+1
    key = subscription, target, name, order
    adapters = implied.get(key)
    if adapters is None:
        adapters = {}
        implied[key] = adapters

    key = key, interfaces # The full key has all 5
    if key not in registered or registered[key].extends(provided):
        # This is either a new entry or it is an entry for a more
        # general interface that is closer provided than what we had
        # before
        registered[key] = provided
        adapters[interfaces] = factories

    for b in target.__bases__:
        _add_multi_adapter(interfaces, name, b, provided, implied,
                           registered, factories, subscription)
