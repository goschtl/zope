USAGE
=====

If you want to use a zope component in different contexts you typically have
to perform numerous steps. A typical use of an adapter in tests and real world
contexts requires the following steps:

    1. define an interface,
    2. write the class resp. implementation,
    3. declare that the class implements the interface, 
    4. declare what the class adapts,
    5. write a test registration for doctests and unittests,
    6. configure the adapter in zcml for a usage outside tests.
    
The 'usage' package automates steps 5 and 6 to a large degree. If you declare
the usage of components directly in the classes you can register all
described components of a module with a single call.

Using an adapter
----------------

The usual pattern goes like this. You write a component with a basic
behavior:

>>> import zope.interface
>>> import zope.component
>>> class IAdaptMe(zope.interface.Interface) :
...     def cry() : pass

>>> class AdaptMe(object) :
...     zope.interface.implements(IAdaptMe)
...     def cry(self) : print "Please, please adapt me."

>>> adaptMe = AdaptMe()
>>> adaptMe.cry()
Please, please adapt me.

You want an adapter that modifies or replaces the behavior :

>>> class IAdapter(zope.interface.Interface) :
...     def lull() : pass

>>> class Adapter(object) :
...     zope.interface.implements(IAdapter)
...     zope.component.adapts(IAdaptMe)
...
...     def __init__(self, context) :
...         self.context = context
...     def lull(self) :
...         self.context.cry()
...         print "Don't worry"

Let's test whether the implementation works:

>>> Adapter(adaptMe).lull()
Please, please adapt me.
Don't worry

We can use the implementation with a single call:

>>> import zorg.usage
>>> zorg.usage.AdapterUsage(Adapter).register()

>>> adapter = IAdapter(adaptMe)
>>> adapter.lull()
Please, please adapt me.
Don't worry

That after all is not very different from calling zope.component.provideAdapter.
The interesting part is that we can declare the usage in the class itself
and register all usages of a module with a single call. With n adapters in
a single module you can safe the typing of n test registrations and n zcml
adapter statements.

The ensureRegistrations function collects all usage descriptions in a single
module and registers them:

>>> zorg.usage.ensureRegistrations("zorg.usage.testcomponent")

>>> from zorg.usage.testcomponent import First, Second
>>> from zorg.usage.testcomponent import ICounter, IIncrement

>>> incr = IIncrement(First())
>>> incr.incr()
2

>>> from zope.app import zapi
>>> counter = zapi.getMultiAdapter((First(), Second()), ICounter)
>>> counter.count()
1
2

>>> roman = zapi.getMultiAdapter((First(), Second()), ICounter, name="roman")
>>> roman.count()
I
II

Since the testcomponent module also describes the use of the latter class as a 
utility we can get the same behavior in a different way:

>>> counter = zapi.getUtility(ICounter, name="verbal")
>>> counter.count()
one
two