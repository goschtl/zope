========
Freezing
========

This package implements basic functionality for freezing objects:
spellings to query whether an object can be frozen, to query whether it
has been frozen, and to actually freeze an object. Further policies may
be implemented above the basic code in this package; and much of the
code in this package is offered as pluggable choices which can be
omitted while still keeping the basic API.

To discover whether an object is freezable, client code should ask if it
provides zc.freeze.interfaces.IFreezable.

Site configurations or code that declares that an object is IFreezable
is assuring that the object provides or can be adaptable to
zc.freeze.interfaces.IFreezing.  This interface has only three elements:
_z_frozen is a readonly boolean that returns whether the object has been
versioned; _z_freeze_datetime is a readonly datetime in pytz.utc
specifying when the object was frozen (or None, if it is not yet
frozen); and _z_freeze is a method that actually freezes the object.  If
the object is already frozen, it raises
zc.freeze.interfaces.FrozenError.  If the object is not in a state to be
frozen, it may raise zc.freeze.interfaces.FreezeError. If the freezing
may succeed, the method should send a
zc.freeze.interfaces.IObjectFrozenEvent (such as
zc.freeze.interfaces.ObjectFrozenEvent).

That's the heart of the package: an API and an agreement, with nothing to test
directly.  One policy that this package does not directly support is that
freezing an object might first create a copy and then version the copy
rather than the original; or version the original but replace the copy in the
location of the original; or make any other choices.  These approaches are
intended to be implemented on top of--above--the zc.freeze API.  This
package provides much simpler capabilities.

Conveniences
============

The package does provide two default implementations of IFreezing, and a few
conveniences.

One IFreezing implementation is for objects that are directly aware of this
API (as opposed to having the functionality assembled from adapters and other
components).

    >>> import zc.freeze
    >>> v = zc.freeze.Freezing()
    >>> from zc.freeze import interfaces
    >>> from zope.interface.verify import verifyObject
    >>> verifyObject(interfaces.IFreezing, v)
    True
    >>> verifyObject(interfaces.IFreezable, v)
    True
    >>> v._z_frozen
    False
    >>> v._z_frozen = True
    Traceback (most recent call last):
    ...
    AttributeError: can't set attribute
    >>> import pytz
    >>> import datetime
    >>> before = datetime.datetime.now(pytz.utc)
    >>> v._z_freeze()
    >>> before <= v._z_freeze_timestamp <= datetime.datetime.now(pytz.utc)
    True
    >>> v._z_frozen
    True
    >>> interfaces.IObjectFrozenEvent.providedBy(events[-1])
    True
    >>> events[-1].object is v
    True
    >>> v._z_freeze()
    Traceback (most recent call last):
    ...
    FrozenError

Another available implementation is an adapter, and stores the information in
an annotation.  Here's a quick demo.

    >>> import zope.annotation.interfaces
    >>> from zope import interface, component
    >>> class Demo(object):
    ...     interface.implements(zope.annotation.interfaces.IAnnotatable)
    ...
    >>> import UserDict
    >>> class DemoAnnotations(UserDict.UserDict):
    ...     interface.implements(zope.annotation.interfaces.IAnnotations)
    ...     component.adapts(Demo)
    ...     def __init__(self, context):
    ...         self.context = context
    ...         self.data = getattr(context, '_z_demo', None)
    ...         if self.data is None:
    ...             self.data = context._z_demo = {}
    ...
    >>> component.provideAdapter(DemoAnnotations)
    >>> component.provideAdapter(zc.freeze.FreezingAdapter)
    >>> d = Demo()
    >>> verifyObject(interfaces.IFreezing, interfaces.IFreezing(d))
    True
    >>> verifyObject(interfaces.IFreezable, interfaces.IFreezing(d))
    True
    >>> interfaces.IFreezing(d)._z_frozen
    False
    >>> interfaces.IFreezing(d)._z_frozen = True
    Traceback (most recent call last):
    ...
    AttributeError: can't set attribute
    >>> before = datetime.datetime.now(pytz.utc)
    >>> interfaces.IFreezing(d)._z_freeze()
    >>> (before <= interfaces.IFreezing(d)._z_freeze_timestamp <=
    ...  datetime.datetime.now(pytz.utc))
    True
    >>> interfaces.IFreezing(d)._z_frozen
    True
    >>> interfaces.IObjectFrozenEvent.providedBy(events[-1])
    True
    >>> events[-1].object is d
    True
    >>> interfaces.IFreezing(d)._z_freeze()
    Traceback (most recent call last):
    ...
    FrozenError

The zc.freeze module also contains three helpers for writing properties and
methods that are freeze-aware.

A 'method' function can generate a freeze-aware method that raises a
FrozenError if the object has been frozen.

'setproperty' and 'delproperty' functions can generate a freeze-aware
descriptor that raises a FrozenError if the set or del methods are called
on a frozen object.  These are rwproperties.

'makeProperty' generates a freeze-aware descriptor that does a simple
get/set but raises FrozenError if the set is attempted on a frozen
object.

    >>> class BiggerDemo(Demo):
    ...     counter = 0
    ...     @zc.freeze.method
    ...     def increase(self):
    ...         self.counter += 1
    ...     _complex = 1
    ...     @property
    ...     def complex_property(self):
    ...         return str(self._complex)
    ...     @zc.freeze.setproperty
    ...     def complex_property(self, value):
    ...         self._complex = value * 2
    ...     zc.freeze.makeProperty('simple_property')
    ...
    >>> d = BiggerDemo()
    >>> d.counter
    0
    >>> d.complex_property
    '1'
    >>> d.simple_property # None
    >>> d.increase()
    >>> d.counter
    1
    >>> d.complex_property = 4
    >>> d.complex_property
    '8'
    >>> d.simple_property = 'hi'
    >>> d.simple_property
    'hi'
    >>> interfaces.IFreezing(d)._z_frozen
    False
    >>> interfaces.IFreezing(d)._z_freeze()
    >>> interfaces.IFreezing(d)._z_frozen
    True
    >>> d.counter
    1
    >>> d.increase()
    Traceback (most recent call last):
    ...
    FrozenError
    >>> d.counter
    1
    >>> d.complex_property
    '8'
    >>> d.complex_property = 10
    Traceback (most recent call last):
    ...
    FrozenError
    >>> d.complex_property
    '8'
    >>> d.simple_property
    'hi'
    >>> d.simple_property = 'bye'
    Traceback (most recent call last):
    ...
    FrozenError
    >>> d.simple_property
    'hi'
