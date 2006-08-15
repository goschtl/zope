====================
Copy Version Control
====================

This package implements basic functionality for one kind of approach for copy-
based version control: spellings to query whether an object can be versioned,
to query whether it has been versioned, and to actually version an object.
Further policies may be implemented above the basic code in this package; and
much of the code in this package is offered as pluggable choices which can be
omitted while still keeping the basic API.

To discover whether an object is versionable, client code should ask if it
provides zc.copyversion.interfaces.IVersionable.

Site configurations or code that declares that an object is IVersionable is
assuring that the object provides or can be adaptable to
zc.copyversion.interfaces.IVersioning.  This interface has only two components:
_z_versioned is a readonly boolean that returns whether the object has been
versioned; and _z_version is a method that actually versions the object.  If
the object is already versioned, it raises
zc.copyversion.interfaces.VersionedError.  If the object is not in a state to
be versioned, it may raise zc.copyversion.interfaces.VersioningError.
If the versioning may succeed, the method should send a
zc.copyversion.interfaces.IObjectVersionedEvent (such as
zc.copyversion.interfaces.ObjectVersionedEvent).

That's the heart of the package: an API and an agreement, with nothing to test
directly.  One policy that this package does not directly support is that
versioning an object might first create a copy and then version the copy
rather than the original; or version the original but replace the copy in the
location of the original; or make any other choices.  These approaches are
intended to be implemented on top of--above--the zc.copyversion API.  This
package provides much simpler capabilities.

Conveniences
============

The package does provide two default implementations of IVersioning, and a few
conveniences.

One IVersioning implementation is for objects that are directly aware of this
API (as opposed to having the functionality assembled from adapters and other
components).

    >>> from zc.copyversion import versioning
    >>> v = versioning.Versioning()
    >>> from zc.copyversion import interfaces
    >>> from zope.interface.verify import verifyObject
    >>> verifyObject(interfaces.IVersioning, v)
    True
    >>> verifyObject(interfaces.IVersionable, v)
    True
    >>> v._z_versioned
    False
    >>> v._z_versioned = True
    Traceback (most recent call last):
    ...
    AttributeError: can't set attribute
    >>> import pytz
    >>> import datetime
    >>> before = datetime.datetime.now(pytz.utc)
    >>> v._z_version()
    >>> before <= v._z_version_timestamp <= datetime.datetime.now(pytz.utc)
    True
    >>> v._z_versioned
    True
    >>> interfaces.IObjectVersionedEvent.providedBy(events[-1])
    True
    >>> events[-1].object is v
    True
    >>> v._z_version()
    Traceback (most recent call last):
    ...
    VersionedError

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
    >>> component.provideAdapter(versioning.VersioningAdapter)
    >>> d = Demo()
    >>> verifyObject(interfaces.IVersioning, interfaces.IVersioning(d))
    True
    >>> verifyObject(interfaces.IVersionable, interfaces.IVersioning(d))
    True
    >>> interfaces.IVersioning(d)._z_versioned
    False
    >>> interfaces.IVersioning(d)._z_versioned = True
    Traceback (most recent call last):
    ...
    AttributeError: can't set attribute
    >>> before = datetime.datetime.now(pytz.utc)
    >>> interfaces.IVersioning(d)._z_version()
    >>> (before <= interfaces.IVersioning(d)._z_version_timestamp <=
    ...  datetime.datetime.now(pytz.utc))
    True
    >>> interfaces.IVersioning(d)._z_versioned
    True
    >>> from zc.copyversion import interfaces
    >>> interfaces.IObjectVersionedEvent.providedBy(events[-1])
    True
    >>> events[-1].object is d
    True
    >>> interfaces.IVersioning(d)._z_version()
    Traceback (most recent call last):
    ...
    VersionedError

The versioning module also contains three helpers for writing properties and
methods that are version-aware.

A 'method' function can generate a version-aware method that raises a
VersionedError if the object has been versioned.

'setproperty' and 'delproperty' functions can generate a version-aware
descriptor that raises a VersionedError if the set or del methods are called
on a versioned object.  These are rwproperties (see rwproperty.txt; imported
from another project.)

'makeProperty' generates a version-aware descriptor that does a simple
get/set but raises VersionedError if the set is attempted on a versioned
object.

    >>> class BiggerDemo(Demo):
    ...     counter = 0
    ...     @versioning.method
    ...     def increase(self):
    ...         self.counter += 1
    ...     _complex = 1
    ...     @property
    ...     def complex_property(self):
    ...         return str(self._complex)
    ...     @versioning.setproperty
    ...     def complex_property(self, value):
    ...         self._complex = value * 2
    ...     versioning.makeProperty('simple_property')
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
    >>> interfaces.IVersioning(d)._z_versioned
    False
    >>> interfaces.IVersioning(d)._z_version()
    >>> interfaces.IVersioning(d)._z_versioned
    True
    >>> d.counter
    1
    >>> d.increase()
    Traceback (most recent call last):
    ...
    VersionedError
    >>> d.counter
    1
    >>> d.complex_property
    '8'
    >>> d.complex_property = 10
    Traceback (most recent call last):
    ...
    VersionedError
    >>> d.complex_property
    '8'
    >>> d.simple_property
    'hi'
    >>> d.simple_property = 'bye'
    Traceback (most recent call last):
    ...
    VersionedError
    >>> d.simple_property
    'hi'

Finally, it contains a subscriber that uses the zope.locking code to freeze
objects when they are versioned.  When combined with packages such as
zc.tokenpolicy, objects that are not version-aware can still effectively
be governed by the versioned status for user interaction through a security
proxy.

    >>> import zope.locking.utility
    >>> import zope.app.keyreference.interfaces
    >>> import zope.locking.interfaces
    >>> util = zope.locking.utility.TokenUtility()
    >>> component.provideUtility(
    ...     util, provides=zope.locking.interfaces.ITokenUtility)
    >>> class DemoKeyReference(object):
    ...     component.adapts(Demo)
    ...     interface.implements(
    ...         zope.app.keyreference.interfaces.IKeyReference)
    ...     _class_counter = 0
    ...     def __init__(self, context):
    ...         self.context = context
    ...         class_ = type(self)
    ...         self._id = getattr(context, '__demo_key_reference__', None)
    ...         if self._id is None:
    ...             self._id = class_._class_counter
    ...             context.__demo_key_reference__ = self._id
    ...             class_._class_counter += 1
    ...     key_type_id = 'zc.copyversion.README.DemoKeyReference'
    ...     def __call__(self):
    ...         return self.context
    ...     def __hash__(self):
    ...         return (self.key_type_id, self._id)
    ...     def __cmp__(self, other):
    ...         if self.key_type_id == other.key_type_id:
    ...             return cmp(self._id, other._id)
    ...         return cmp(self.key_type_id, other.key_type_id)
    ...
    >>> component.provideAdapter(DemoKeyReference)
    >>> from zc.copyversion import subscribers
    >>> component.provideHandler(subscribers.freezer)
    >>> d = Demo()
    >>> util.get(d) # None
    >>> interfaces.IVersioning(d)._z_version()
    >>> zope.locking.interfaces.IFreeze.providedBy(util.get(d))
    True

Our copyversion story still needs other components.

- copy subscribers account for resetting objectlog and comments across copies.
  These belong in the respective packages.

- UI for making individual objects into frozen versions.  One approach might
  belong in this package at some point.
