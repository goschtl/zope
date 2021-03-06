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
"""Classes to support implenting IContained

$Id$
"""
from zope.proxy import getProxiedObject
from zope.exceptions import DuplicationError
from zope.security.checker import selectChecker, CombinedChecker

import zope.interface
from zope.interface.declarations import ObjectSpecificationDescriptor
from zope.interface.declarations import getObjectSpecification
from zope.interface.declarations import ObjectSpecification
from zope.interface import providedBy

from zope.app.exception.interfaces import UserError
from zope.app.event.objectevent import ObjectEvent, modified
from zope.app.event import publish
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.container.interfaces import IContained
from zope.app.container.interfaces import INameChooser
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectMovedEvent
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.location.interfaces import ILocation
from zope.app.container._zope_app_container_contained import ContainedProxyBase
from zope.app.container._zope_app_container_contained import getProxiedObject

class Contained(object):
    """Stupid mix-in that defines __parent__ and __name__ attributes
    """

    zope.interface.implements(IContained)

    __parent__ = __name__ = None

class ObjectMovedEvent(ObjectEvent):
    """An object has been moved"""

    zope.interface.implements(IObjectMovedEvent)

    def __init__(self, object, oldParent, oldName, newParent, newName):
        ObjectEvent.__init__(self, object)
        self.oldParent = oldParent
        self.oldName = oldName
        self.newParent = newParent
        self.newName = newName

class ObjectAddedEvent(ObjectMovedEvent):
    """An object has been added to a container"""

    zope.interface.implements(IObjectAddedEvent)

    def __init__(self, object, newParent=None, newName=None):
        if newParent is None:
            newParent = object.__parent__
        if newName is None:
            newName = object.__name__
        ObjectMovedEvent.__init__(self, object, None, None, newParent, newName)

class ObjectRemovedEvent(ObjectMovedEvent):
    """An object has been removed from a container"""

    zope.interface.implements(IObjectRemovedEvent)

    def __init__(self, object, oldParent=None, oldName=None):
        if oldParent is None:
            oldParent = object.__parent__
        if oldName is None:
            oldName = object.__name__
        ObjectMovedEvent.__init__(self, object, oldParent, oldName, None, None)


def containedEvent(object, container, name=None):
    """Establish the containment of the object in the container

    The object and necessary event are returned. The object may be a
    ContainedProxy around the original object. The event is an added
    event, a moved event, or None.

    If the object implements IContained, simply set its __parent__
    and __name__ attributes:

        >>> container = {}
        >>> item = Contained()
        >>> x, event = containedEvent(item, container, u'foo')
        >>> x is item
        True
        >>> item.__parent__ is container
        True
        >>> item.__name__
        u'foo'

    We have an added event:

        >>> event.__class__.__name__
        'ObjectAddedEvent'
        >>> event.object is item
        True
        >>> event.newParent is container
        True
        >>> event.newName
        u'foo'
        >>> event.oldParent
        >>> event.oldName

    Now if we call contained again:

        >>> x2, event = containedEvent(item, container, u'foo')
        >>> x2 is item
        True
        >>> item.__parent__ is container
        True
        >>> item.__name__
        u'foo'
    
    We don't get a new added event:

        >>> event

    If the object already had a parent but the parent or name was
    different, we get a moved event:

        >>> x, event = containedEvent(item, container, u'foo2')
        >>> event.__class__.__name__
        'ObjectMovedEvent'
        >>> event.object is item
        True
        >>> event.newParent is container
        True
        >>> event.newName
        u'foo2'
        >>> event.oldParent is container
        True
        >>> event.oldName
        u'foo'

    If the object implements ILocation, but not IContained, set it's
    __parent__ and __name__ attributes *and* declare that it
    implements IContained:

        >>> from zope.app.location import Location
        >>> item = Location()
        >>> IContained.providedBy(item)
        False
        >>> x, event = containedEvent(item, container, 'foo')
        >>> x is item
        True
        >>> item.__parent__ is container
        True
        >>> item.__name__
        'foo'
        >>> IContained.providedBy(item)
        True


    If the object doesn't even implement ILocation, put a
    ContainedProxy around it:

        >>> item = []
        >>> x, event = containedEvent(item, container, 'foo')
        >>> x is item
        False
        >>> x.__parent__ is container
        True
        >>> x.__name__
        'foo'
    """

    if not IContained.providedBy(object):
        if ILocation.providedBy(object):
            zope.interface.directlyProvides(object, IContained)
        else:
            object = ContainedProxy(object)

    oldparent = object.__parent__
    oldname = object.__name__

    if oldparent is container and oldname == name:
        # No events
        return object, None

    object.__parent__ = container
    object.__name__ = name

    if oldparent is None or oldname is None:
        event = ObjectAddedEvent(object, container, name)
    else:
        event = ObjectMovedEvent(object, oldparent, oldname, container, name)

    return object, event

def contained(object, container, name=None):
    """Establish the containment of the object in the container

    Just return the contained object without an event. This is a convenience
    "macro" for:

       containedEvent(object, container, name)[0]

    This function is only used for tests.
    """
    return containedEvent(object, container, name)[0]

def setitem(container, setitemf, name, object):
    """Helper function to set an item and generate needed events

    This helper is needed, in part, because the events need to get
    published after the object has been added to the container.

    If the item implements IContained, simply set it's __parent__
    and __name attributes:

    >>> class IItem(zope.interface.Interface):
    ...     pass
    >>> class Item(Contained):
    ...     zope.interface.implements(IItem)
    ...     def setAdded(self, event):
    ...         self.added = event
    ...     def setMoved(self, event):
    ...         self.moved = event

    >>> from zope.app.event.objectevent import objectEventCallbackHelper
    >>> from zope.app.container.interfaces import IObjectAddedEvent
    >>> from zope.app.container.interfaces import IObjectMovedEvent
    >>> from zope.component import getService
    >>> from zope.app.servicenames import Adapters
    >>> from zope.app.event.interfaces import ISubscriber
    >>> factory = objectEventCallbackHelper(
    ...     lambda event: event.object.setAdded(event))
    >>> getService(None, Adapters).subscribe(
    ...     [IItem,IObjectAddedEvent], ISubscriber, factory)
    >>> factory = objectEventCallbackHelper(
    ...     lambda event: event.object.setMoved(event))
    >>> getService(None, Adapters).subscribe(
    ...     [IItem, IObjectMovedEvent], ISubscriber, factory)
    >>> item = Item()

    >>> container = {}
    >>> setitem(container, container.__setitem__, u'c', item)
    >>> container[u'c'] is item
    1
    >>> item.__parent__ is container
    1
    >>> item.__name__
    u'c'

    If we run this using the testing framework, we'll use getEvents to
    track the events generated:

    >>> from zope.app.event.tests.placelesssetup import getEvents
    >>> from zope.app.event.interfaces import IObjectModifiedEvent

    We have an added event:

    >>> len(getEvents(IObjectAddedEvent))
    1
    >>> event = getEvents(IObjectAddedEvent)[-1]
    >>> event.object is item
    1
    >>> event.newParent is container
    1
    >>> event.newName
    u'c'
    >>> event.oldParent
    >>> event.oldName

    As well as a modification event for the container:

    >>> len(getEvents(IObjectModifiedEvent))
    1
    >>> getEvents(IObjectModifiedEvent)[-1].object is container
    1

    The item's hooks have been called:

    >>> item.added is event
    1
    >>> item.moved is event
    1

    We can suppress events and hooks by setting the __parent__ and
    __name__ first:

    >>> item = Item()
    >>> item.__parent__, item.__name__ = container, 'c2'
    >>> setitem(container, container.__setitem__, u'c2', item)
    >>> len(container)
    2
    >>> len(getEvents(IObjectAddedEvent))
    1
    >>> len(getEvents(IObjectModifiedEvent))
    1

    >>> getattr(item, 'added', None)
    >>> getattr(item, 'moved', None)

    If the item had a parent or name (as in a move or rename),
    we generate a move event, rather than an add event:

    >>> setitem(container, container.__setitem__, u'c3', item)
    >>> len(container)
    3
    >>> len(getEvents(IObjectAddedEvent))
    1
    >>> len(getEvents(IObjectModifiedEvent))
    2
    >>> len(getEvents(IObjectMovedEvent))
    2

    (Note that we have 2 move events because add are move events.)

    We also get the move hook called, but not the add hook:

    >>> event = getEvents(IObjectMovedEvent)[-1]
    >>> getattr(item, 'added', None)
    >>> item.moved is event
    1

    If we try to replace an item without deleting it first, we'll get
    an error:

    >>> setitem(container, container.__setitem__, u'c', [])
    Traceback (most recent call last):
    ...
    DuplicationError: c


    >>> del container[u'c']
    >>> setitem(container, container.__setitem__, u'c', [])
    >>> len(getEvents(IObjectAddedEvent))
    2
    >>> len(getEvents(IObjectModifiedEvent))
    3


    If the object implements ILocation, but not IContained, set it's
    __parent__ and __name__ attributes *and* declare that it
    implements IContained:

    >>> from zope.app.location import Location
    >>> item = Location()
    >>> IContained.providedBy(item)
    0
    >>> setitem(container, container.__setitem__, u'l', item)
    >>> container[u'l'] is item
    1
    >>> item.__parent__ is container
    1
    >>> item.__name__
    u'l'
    >>> IContained.providedBy(item)
    1

    We get new added and modification events:

    >>> len(getEvents(IObjectAddedEvent))
    3
    >>> len(getEvents(IObjectModifiedEvent))
    4

    If the object doesn't even implement ILocation, put a
    ContainedProxy around it:

    >>> item = []
    >>> setitem(container, container.__setitem__, u'i', item)
    >>> container[u'i']
    []
    >>> container[u'i'] is item
    0
    >>> item = container[u'i']
    >>> item.__parent__ is container
    1
    >>> item.__name__
    u'i'
    >>> IContained.providedBy(item)
    1

    >>> len(getEvents(IObjectAddedEvent))
    4
    >>> len(getEvents(IObjectModifiedEvent))
    5

    We'll get type errors if we give keys that aren't unicode or ascii keys:

    >>> setitem(container, container.__setitem__, 42, item)
    Traceback (most recent call last):
    ...
    TypeError: name not unicode or ascii string

    >>> setitem(container, container.__setitem__, None, item)
    Traceback (most recent call last):
    ...
    TypeError: name not unicode or ascii string

    >>> setitem(container, container.__setitem__, 'hello ' + chr(200), item)
    Traceback (most recent call last):
    ...
    TypeError: name not unicode or ascii string

    and we'll get a value error of we give an empty string or unicode:

    >>> setitem(container, container.__setitem__, '', item)
    Traceback (most recent call last):
    ...
    ValueError: empty names are not allowed

    >>> setitem(container, container.__setitem__, u'', item)
    Traceback (most recent call last):
    ...
    ValueError: empty names are not allowed

    """

    # Do basic name check:
    if isinstance(name, str):
        try:
            name = unicode(name)
        except UnicodeError:
            raise TypeError("name not unicode or ascii string")
    elif not isinstance(name, unicode):
        raise TypeError("name not unicode or ascii string")

    if not name:
        raise ValueError("empty names are not allowed")

    old = container.get(name)
    if old is object:
        return
    if old is not None:
        raise DuplicationError(name)

    object, event = containedEvent(object, container, name)
    setitemf(name, object)
    if event:
        publish(container, event)
        modified(container)

fixing_up = False
def uncontained(object, container, name=None):
    """Clear the containment relationship between the object amd the container

    If we run this using the testing framework, we'll use getEvents to
    track the events generated:

    >>> from zope.app.event.tests.placelesssetup import getEvents
    >>> from zope.app.container.interfaces import IObjectRemovedEvent
    >>> from zope.app.event.interfaces import IObjectModifiedEvent

    We'll start by creating a container with an item:

    >>> class Item(Contained):
    ...     pass

    >>> item = Item()
    >>> container = {u'foo': item}
    >>> x, event = containedEvent(item, container, u'foo')
    >>> item.__parent__ is container
    1
    >>> item.__name__
    u'foo'

    Now we'll remove the item. It's parent and name are cleared:

    >>> uncontained(item, container, u'foo')
    >>> item.__parent__
    >>> item.__name__

    We now have a new removed event:

    >>> len(getEvents(IObjectRemovedEvent))
    1
    >>> event = getEvents(IObjectRemovedEvent)[-1]
    >>> event.object is item
    1
    >>> event.oldParent is container
    1
    >>> event.oldName
    u'foo'
    >>> event.newParent
    >>> event.newName

    As well as a modification event for the container:

    >>> len(getEvents(IObjectModifiedEvent))
    1
    >>> getEvents(IObjectModifiedEvent)[-1].object is container
    1

    Now if we call uncontained again:

    >>> uncontained(item, container, u'foo')

    We won't get any new events, because __parent__ and __name__ are None:

    >>> len(getEvents(IObjectRemovedEvent))
    1
    >>> len(getEvents(IObjectModifiedEvent))
    1

    But, if either the name or parent are not None and they are not
    the container and the old name, we'll get a modified event but not
    a removed event.

    >>> item.__parent__, item.__name__ = container, None
    >>> uncontained(item, container, u'foo')
    >>> len(getEvents(IObjectRemovedEvent))
    1
    >>> len(getEvents(IObjectModifiedEvent))
    2

    >>> item.__parent__, item.__name__ = None, u'bar'
    >>> uncontained(item, container, u'foo')
    >>> len(getEvents(IObjectRemovedEvent))
    1
    >>> len(getEvents(IObjectModifiedEvent))
    3

    """
    try:
        oldparent = object.__parent__
        oldname = object.__name__
    except AttributeError:
        # The old object doesn't implements IContained
        # Maybe we're converting old data:
        if not fixing_up:
            raise
        oldparent = None
        oldname = None

    if oldparent is not container or oldname != name:
        if oldparent is not None or oldname is not None:
            modified(container)
        return

    event = ObjectRemovedEvent(object, oldparent, oldname)
    publish(container, event)

    object.__parent__ = None
    object.__name__ = None
    modified(container)

class NameChooser:

    zope.interface.implements(INameChooser)

    def __init__(self, context):
        self.context = context

    def checkName(self, name, object):
        "See zope.app.container.interfaces.INameChooser"

        if not name:
            raise UserError(
                _("An empty name was provided. Names cannot be empty.")
                )

        if isinstance(name, str):
            name = unicode(name)
        elif not isinstance(name, unicode):
            raise TypeError("Invalid name type", type(name))

        if name[:1] in '+@' or '/' in name:
            raise UserError(
                _("Names cannot begin with '+' or '@' or contain '/'")
                )

        if name in self.context:
            raise UserError(
                _("The given name is already being used")
                )

        return True


    def chooseName(self, name, object):
        "See zope.app.container.interfaces.INameChooser"

        container = self.context

        if not name:
            name = object.__class__.__name__

        dot = name.rfind('.')
        if dot >= 0:
            suffix = name[dot:]
            name = name[:dot]
        else:
            suffix = ''


        n = name + suffix
        i = 1
        while n in container:
            i += 1
            n = name + u'-' + unicode(i) + suffix

        # Make sure tha name is valid.  We may have started with something bad.
        self.checkName(n, object)

        return n


class DecoratorSpecificationDescriptor(ObjectSpecificationDescriptor):
    """Support for interface declarations on decorators

    >>> from zope.interface import *
    >>> class I1(Interface):
    ...     pass
    >>> class I2(Interface):
    ...     pass
    >>> class I3(Interface):
    ...     pass
    >>> class I4(Interface):
    ...     pass

    >>> class D1(ContainedProxy):
    ...   implements(I1)


    >>> class D2(ContainedProxy):
    ...   implements(I2)

    >>> class X:
    ...   implements(I3)

    >>> x = X()
    >>> directlyProvides(x, I4)

    Interfaces of X are ordered with the directly-provided interfaces first

    >>> [interface.getName() for interface in list(providedBy(x))]
    ['I4', 'I3']

    When we decorate objects, what order should the interfaces come
    in?  One could argue that decorators are less specific, so they
    should come last.

    >>> [interface.getName() for interface in list(providedBy(D1(x)))]
    ['I4', 'I3', 'I1', 'IContained', 'IPersistent']

    >>> [interface.getName() for interface in list(providedBy(D2(D1(x))))]
    ['I4', 'I3', 'I1', 'IContained', 'IPersistent', 'I2']
    """
    def __get__(self, inst, cls=None):
        if inst is None:
            return getObjectSpecification(cls)
        else:
            provided = providedBy(getProxiedObject(inst))

            # Use type rather than __class__ because inst is a proxy and
            # will return the proxied object's class.
            cls = type(inst)
            return ObjectSpecification(provided, cls)


class DecoratedSecurityCheckerDescriptor(object):
    """Descriptor for a Decorator that provides a decorated security checker.
    """
    def __get__(self, inst, cls=None):
        if inst is None:
            return self
        else:
            proxied_object = getProxiedObject(inst)
            checker = getattr(proxied_object, '__Security_checker__', None)
            if checker is None:
                checker = selectChecker(proxied_object)
            wrapper_checker = selectChecker(inst)
            if wrapper_checker is None:
                return checker
            elif checker is None:
                return wrapper_checker
            else:
                return CombinedChecker(wrapper_checker, checker)


class ContainedProxy(ContainedProxyBase):

    __safe_for_unpickling__ = True

    zope.interface.implements(IContained)

    __providedBy__ = DecoratorSpecificationDescriptor()

    __Security_checker__ = DecoratedSecurityCheckerDescriptor()



