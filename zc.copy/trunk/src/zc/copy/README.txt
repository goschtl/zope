=======
zc.copy
=======

The copier module has two main components: a generic replacement for
zope.location.pickling.locationCopy called zc.copy.copy, and a
replacement for zope.copypastemove.ObjectCopier that uses the new copy
function. Additionally, the module contains an adapter for use with the
new copy function that gives the same ILocation behavior as locationCopy.

These three components (the new copy, the new ObjectCopier, and the
ILocation adapter) are appropriate for inclusion in Zope 3, should that be
desired.

The heart of the module, then, is the new copy function.  Like locationCopy,
this function uses pickling to perform the copy; however, instead of the
hard-wired heuristic in locationCopy to determine what should be copied and
what should remain static, this function uses adapters for pluggable behavior.

Also, copy automatically sets __parent__ and __name__ of the object copy
to be None, if values exist for them.  If you do not want this behavior,
a `clone` method does not include this logic.  For most use with classic
Zope 3 locations, however, you will want to use `copy`.  We'll look a
bit at both functions in this document.

The clone function (and thus the copy function that wraps clone) uses
pickle to copy the object and all its subobjects recursively.  As each
object and subobject is pickled, the function tries to adapt it to
zc.copy.interfaces.ICopyHook. If a copy hook is found, the recursive
copy is halted.  The hook is called with two values: the main, top-level
object that is being copied; and a callable that supports registering
functions to be called after the copy is made. The copy hook should
return the exact object or subobject that should be used at this point
in the copy, or raise zc.copy.interfaces.ResumeCopy to resume copying
the object or subobject recursively after all.

We'll examine the callable a bit later: first let's examine a simple
use.  A simple hook is to support the use case of resetting the state of
data that should be changed in a copy--for instance, a log, or freezing or
versioning data.  The canonical way to do this is by storing the changable
data on a special sub-object of the object that is to be copied.  We'll
look at a simple case of a subobject that should be converted to None when it
is copied--the way that the zc.freeze copier hook works.  Also see the
zc.objectlog copier module for a similar example.

So, here is a simple object that stores a boolean on a special object.

    >>> class Demo(object):
    ...     _frozen = None
    ...     def isFrozen(self):
    ...         return self._frozen is not None
    ...     def freeze(self):
    ...         self._frozen = Data()
    ...
    >>> class Data(object):
    ...     pass
    ...

Here's what happens if we copy one of these objects without a copy hook.

    >>> original = Demo()
    >>> original.isFrozen()
    False
    >>> original.freeze()
    >>> original.isFrozen()
    True
    >>> import zc.copy
    >>> copy = zc.copy.copy(original)
    >>> copy is original
    False
    >>> copy.isFrozen()
    True

Now let's make a super-simple copy hook that always returns None, no
matter what the main location being copied is.  We'll register it and
make another copy.

    >>> import zope.component
    >>> import zope.interface
    >>> import zc.copy.interfaces
    >>> def _factory(location, register):
    ...     return None
    >>> @zope.component.adapter(Data)
    ... @zope.interface.implementer(zc.copy.interfaces.ICopyHook)
    ... def data_copyfactory(obj):
    ...     return _factory
    ...

    >>> zope.component.provideAdapter(data_copyfactory)
    >>> copy2 = zc.copy.copy(original)
    >>> copy2 is original
    False
    >>> copy2.isFrozen()
    False

Much better.

The ILocation adapter is just a tiny bit more complicated.  Look in
__init__.py at location_copyfactory.  Here, if the object implements
ILocation and is not 'inside' the main object being copied, it is used
directly, and not copied.  Otherwise, the hook raises ResumeCopy to
cancel itself.

[the following is adapted from a doctest in zope.location.pickling]

For example, suppose we have an object (location) hierarchy like this::

           o1
          /  \
        o2    o3
        |     |
        o4    o5

    >>> from zope.location.location import Location
    >>> o1 = Location()
    >>> o1.o2 = Location(); o1.o2.__parent__ = o1
    >>> o1.o3 = Location(); o1.o3.__parent__ = o1
    >>> o1.o2.o4 = Location(); o1.o2.o4.__parent__ = o1.o2
    >>> o1.o3.o5 = Location(); o1.o3.o5.__parent__ = o1.o3

In addition, o3 has a non-location reference to o4.

    >>> o1.o3.o4 = o1.o2.o4

When we copy o3, we want to get a copy of o3 and o5, with
references to o1 and o4.  Without our adapter, this won't happen.

    >>> c3 = zc.copy.copy(o1.o3)
    >>> c3 is o1.o3 # it /is/ a copy
    False
    >>> o1.o3.o4 is o1.o2.o4
    True
    >>> c3.o4 is o1.o2.o4
    False

The c3.__parent__ will be None, because we used copy, rather than clone.

    >>> o1.o3.__parent__ is o1
    True
    >>> c3.__parent__ is None
    True

If we had used clone, then the __parent__ would also have been included.

    >>> another3 = zc.copy.clone(o1.o3)
    >>> another3.__parent__ is o1 # the __parent__ has also been copied.
    False
    >>> another3.__parent__ is None
    False

In Zope 3, that would effectively mean that any object that was transitively
linked with __parent__ links to the root of the Zope application would get the
*entire Zope database* copied.  Not good.  Using the `clone` method, you'll
see the objects; the `copy` method still makes the copy, but rips it off at the
end, so it can be *very* inefficient.  And in fact, with our first c3, we do
have a copy of o1, just hidden away.

    >>> o1.o3.o4.__parent__.__parent__ is o1
    True
    >>> c3.o4.__parent__.__parent__ is o1
    False
    >>> c3.o4.__parent__.__parent__ is None
    False

How can we fix all this?  Register our adapter and the results are as we wish.

    >>> zope.component.provideAdapter(
    ...     zc.copy.location_copyfactory)
    >>> c3 = zc.copy.copy(o1.o3)
    >>> c3 is o1.o3
    False
    >>> c3.__parent__ is None # because we used `copy`, not `clone`
    True
    >>> c3.o4 is o1.o2.o4
    True
    >>> c3.o5 is o1.o3.o5
    False
    >>> c3.o5.__parent__ is c3
    True

If we used clone, then we could see that the adapter also handled c3.__parent__
the right way.

    >>> another3 = zc.copy.clone(o1.o3)
    >>> another3.__parent__ is o1
    True

[end variation of zope.location.pickling test]

Our final step in the tour of the copy method is to look at the registration
function that the hook can use.  It is useful for resetting objects within the
new copy--for instance, back references such as __parent__ pointers.  This is
used concretely in the zc.objectlog.copier module; we will come up with a
similar but artificial example here.

Imagine an object with a subobject that is "located" (i.e., zope.location) on
the parent and should be replaced whenever the main object is copied.

    >>> class Subobject(Location):
    ...     def __init__(self):
    ...         self.counter = 0
    ...     def __call__(self):
    ...         res = self.counter
    ...         self.counter += 1
    ...         return res
    ...
    >>> o = Location()
    >>> s = Subobject()
    >>> import zope.location.location
    >>> o.subobject = s
    >>> zope.location.locate(s, o, 'subobject')
    >>> s.__parent__ is o
    True
    >>> o.subobject()
    0
    >>> o.subobject()
    1
    >>> o.subobject()
    2

Without an ICopyHook, this will simply duplicate the subobject, with correct
new pointers.

    >>> c = zc.copy.copy(o)
    >>> c.subobject.__parent__ is c
    True

Note that the subobject has also copied state.

    >>> c.subobject()
    3
    >>> o.subobject()
    3

Our goal will be to make the counters restart when they are copied.  We'll do
that with a copy hook.

This copy hook is different: it provides an object to replace the old object,
but then it needs to set it up further after the copy is made.  This is
accomplished by registering a callable, `reparent` here, that sets up the
__parent__.  The callable is passed a function that can translate something
from the original object into the equivalent on the new object.  We use this
to find the new parent, so we can set it.

    >>> import zope.component
    >>> import zope.interface
    >>> import zc.copy.interfaces
    >>> @zope.component.adapter(Subobject)
    ... @zope.interface.implementer(zc.copy.interfaces.ICopyHook)
    ... def subobject_copyfactory(original):
    ...     def factory(location, register):
    ...         obj = Subobject()
    ...         def reparent(translate):
    ...             obj.__parent__ = translate(original.__parent__)
    ...         register(reparent)
    ...         return obj
    ...     return factory
    ...
    >>> zope.component.provideAdapter(subobject_copyfactory)

Now when we copy, the new subobject will have the correct, revised __parent__,
but will be otherwise reset (here, just the counter)

    >>> c = zc.copy.copy(o)
    >>> c.subobject.__parent__ is c
    True
    >>> c.subobject()
    0
    >>> o.subobject()
    4

ObjectCopier
============

The ObjectCopier in the copier module is simply a variation on the
ObjectCopier in zope.copypastemove, with the change that it uses the
zc.copy.copy function rather than zope.location.pickling.locationCopy. 
With the location-based copy hook described above already installed, the
copier should have the same behavior. In that vein, the following is
adapted from the test in zope/copypastemove/__init__.py.

To use an object copier, pass a contained `object` to the class.
The contained `object` should implement `IContained`.  It should be
contained in a container that has an adapter to `INameChooser`.

    >>> from zope.copypastemove import ExampleContainer
    >>> from zope.app.container.contained import Contained
    >>> ob = Contained()
    >>> container = ExampleContainer()
    >>> container[u'foo'] = ob
    >>> copier = zc.copy.ObjectCopier(ob)

In addition to moving objects, object copiers can tell you if the
object is movable:

    >>> copier.copyable()
    True

which, at least for now, they always are.  A better question to
ask is whether we can copy to a particular container. Right now,
we can always copy to a container of the same class:

    >>> container2 = ExampleContainer()
    >>> copier.copyableTo(container2)
    True
    >>> copier.copyableTo({})
    Traceback (most recent call last):
    ...
    TypeError: Container is not a valid Zope container.

Of course, once we've decided we can copy an object, we can use
the copier to do so:

    >>> copier.copyTo(container2)
    u'foo'
    >>> list(container)
    [u'foo']
    >>> list(container2)
    [u'foo']
    >>> ob.__parent__ is container
    True
    >>> container2[u'foo'] is ob
    False
    >>> container2[u'foo'].__parent__ is container2
    True
    >>> container2[u'foo'].__name__
    u'foo'

We can also specify a name:

    >>> copier.copyTo(container2, u'bar')
    u'bar'
    >>> l = list(container2)
    >>> l.sort()
    >>> l
    [u'bar', u'foo']

    >>> ob.__parent__ is container
    True
    >>> container2[u'bar'] is ob
    False
    >>> container2[u'bar'].__parent__ is container2
    True
    >>> container2[u'bar'].__name__
    u'bar'

But we may not use the same name given, if the name is already in
use:

    >>> copier.copyTo(container2, u'bar')
    u'bar_'
    >>> l = list(container2)
    >>> l.sort()
    >>> l
    [u'bar', u'bar_', u'foo']
    >>> container2[u'bar_'].__name__
    u'bar_'


If we try to copy to an invalid container, we'll get an error:

    >>> copier.copyTo({})
    Traceback (most recent call last):
    ...
    TypeError: Container is not a valid Zope container.

Do a test for preconditions:

    >>> import zope.interface
    >>> import zope.schema
    >>> def preNoZ(container, name, ob):
    ...     "Silly precondition example"
    ...     if name.startswith("Z"):
    ...         raise zope.interface.Invalid("Invalid name.")

    >>> class I1(zope.interface.Interface):
    ...     def __setitem__(name, on):
    ...         "Add an item"
    ...     __setitem__.precondition = preNoZ

    >>> from zope.app.container.interfaces import IContainer
    >>> class C1(object):
    ...     zope.interface.implements(I1, IContainer)
    ...     def __repr__(self):
    ...         return 'C1'

    >>> container3 = C1()
    >>> copier.copyableTo(container3, 'ZDummy')
    False
    >>> copier.copyableTo(container3, 'newName')
    True

And a test for constraints:

    >>> def con1(container):
    ...     "silly container constraint"
    ...     if not hasattr(container, 'x'):
    ...         return False
    ...     return True
    ...
    >>> class I2(zope.interface.Interface):
    ...     __parent__ = zope.schema.Field(constraint=con1)
    ...
    >>> class constrainedObject(object):
    ...     zope.interface.implements(I2)
    ...     def __init__(self):
    ...         self.__name__ = 'constrainedObject'
    ...
    >>> cO = constrainedObject()
    >>> copier2 = zc.copy.ObjectCopier(cO)
    >>> copier2.copyableTo(container)
    False
    >>> container.x = 1
    >>> copier2.copyableTo(container)
    True
