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

$Id: __init__.py,v 1.8 2004/04/27 10:53:46 jim Exp $
"""
import zope.interface
from zope.app.location.interfaces import ILocation
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.traversing.interfaces import ITraverser
from zope.app.site.interfaces import ISite
from zope.proxy import removeAllProxies
from zope.proxy import ProxyBase, getProxiedObject
from zope.app.decorator import DecoratorSpecificationDescriptor
from zope.app.decorator import DecoratedSecurityCheckerDescriptor
from zope.app.traversing import getParents

import cPickle
import tempfile

class Location(object):
    """Stupid mix-in that defines __parent__ and __name__ attributes
    """

    zope.interface.implements(ILocation)

    __parent__ = __name__ = None

def locate(object, parent, name=None):
    """Locate an object in another

    This method should only be called from trusted code, because it
    sets attributes that are normally unsettable.
    """

    object = removeAllProxies(object)
    object.__parent__ = parent
    object.__name__ = name



def LocationIterator(object):
    while object is not None:
        yield object
        object = getattr(object, '__parent__', None)

class LocationPhysicallyLocatable:
    """Provide location information for location objects
    """

    zope.interface.implements(IPhysicallyLocatable)

    def __init__(self, context):
        self.context = context

    def getRoot(self):
        """Get the root location for a location.

        See IPhysicallyLocatable

        The root location is a location that contains the given
        location and that implements IContainmentRoot.

        >>> root = Location()
        >>> zope.interface.directlyProvides(root, IContainmentRoot)
        >>> LocationPhysicallyLocatable(root).getRoot() is root
        1

        >>> o1 = Location(); o1.__parent__ = root
        >>> LocationPhysicallyLocatable(o1).getRoot() is root
        1

        >>> o2 = Location(); o2.__parent__ = o1
        >>> LocationPhysicallyLocatable(o2).getRoot() is root
        1

        We'll get a TypeError if we try to get the location fo a
        rootless object:

        >>> o1.__parent__ = None
        >>> LocationPhysicallyLocatable(o1).getRoot()
        Traceback (most recent call last):
        ...
        TypeError: Not enough context to determine location root
        >>> LocationPhysicallyLocatable(o2).getRoot()
        Traceback (most recent call last):
        ...
        TypeError: Not enough context to determine location root

        If we screw up and create a location cycle, it will be caught:

        >>> o1.__parent__ = o2
        >>> LocationPhysicallyLocatable(o1).getRoot()
        Traceback (most recent call last):
        ...
        TypeError: Maximim location depth exceeded, """ \
                """probably due to a a location cycle.
        """
        context = self.context
        max = 9999
        while context is not None:
            if IContainmentRoot.providedBy(context):
                return context
            context = context.__parent__
            max -= 1
            if max < 1:
                raise TypeError("Maximim location depth exceeded, "
                                "probably due to a a location cycle.")

        raise TypeError("Not enough context to determine location root")

    def getPath(self):
        """Get the path of a location.

        See IPhysicallyLocatable

        This is an "absolute path", rooted at a root object.

        >>> root = Location()
        >>> zope.interface.directlyProvides(root, IContainmentRoot)
        >>> LocationPhysicallyLocatable(root).getPath()
        u'/'

        >>> o1 = Location(); o1.__parent__ = root; o1.__name__ = 'o1'
        >>> LocationPhysicallyLocatable(o1).getPath()
        u'/o1'

        >>> o2 = Location(); o2.__parent__ = o1; o2.__name__ = u'o2'
        >>> LocationPhysicallyLocatable(o2).getPath()
        u'/o1/o2'

        It is an error to get the path of a rootless location:

        >>> o1.__parent__ = None
        >>> LocationPhysicallyLocatable(o1).getPath()
        Traceback (most recent call last):
        ...
        TypeError: Not enough context to determine location root

        >>> LocationPhysicallyLocatable(o2).getPath()
        Traceback (most recent call last):
        ...
        TypeError: Not enough context to determine location root

        If we screw up and create a location cycle, it will be caught:

        >>> o1.__parent__ = o2
        >>> LocationPhysicallyLocatable(o1).getPath()
        Traceback (most recent call last):
        ...
        TypeError: Maximim location depth exceeded, """ \
                """probably due to a a location cycle.

        """

        path = []
        context = self.context
        max = 9999
        while context is not None:
            if IContainmentRoot.providedBy(context):
                if path:
                    path.append('')
                    path.reverse()
                    return u'/'.join(path)
                else:
                    return u'/'
            path.append(context.__name__)
            context = context.__parent__
            max -= 1
            if max < 1:
                raise TypeError("Maximim location depth exceeded, "
                                "probably due to a a location cycle.")

        raise TypeError("Not enough context to determine location root")

    def getName(self):
        """Get a location name

        See IPhysicallyLocatable.

        >>> o1 = Location(); o1.__name__ = 'o1'
        >>> LocationPhysicallyLocatable(o1).getName()
        'o1'

        """
        return self.context.__name__

    def getNearestSite(self):
        """return the nearest site, see IPhysicallyLocatable"""
        if ISite.providedBy(self.context):
            return self.context
        for parent in getParents(self.context):
            if ISite.providedBy(parent):
                return parent
        return self.getRoot()

def inside(l1, l2):
    """Is l1 inside l2

    L1 is inside l2 if l2 is an ancestor of l1.

    >>> o1 = Location()
    >>> o2 = Location(); o2.__parent__ = o1
    >>> o3 = Location(); o3.__parent__ = o2
    >>> o4 = Location(); o4.__parent__ = o3

    >>> inside(o1, o1)
    1
    >>> inside(o2, o1)
    1
    >>> inside(o3, o1)
    1
    >>> inside(o4, o1)
    1

    >>> inside(o1, o4)
    0

    >>> inside(o1, None)
    0

    """

    while l1 is not None:
        if l1 is l2:
            return True
        l1 = l1.__parent__

    return False


def locationCopy(loc):
    """Return a copy of an object,, and anything in it

    If object in the location refer to objects outside of the
    location, then the copies of the objects in the location refer to
    the same outside objects.

    For example, suppose we have an object (location) hierarchy like this:

           o1
          /  \
        o2    o3
        |     |
        o4    o5

    >>> o1 = Location()
    >>> o1.o2 = Location(); o1.o2.__parent__ = o1
    >>> o1.o3 = Location(); o1.o3.__parent__ = o1
    >>> o1.o2.o4 = Location(); o1.o2.o4.__parent__ = o1.o2
    >>> o1.o3.o5 = Location(); o1.o3.o5.__parent__ = o1.o3

    In addition, o3 has a non-locatin reference to o4.

    >>> o1.o3.o4 = o1.o2.o4

    When we copy o3, we should get a copy of o3 and o5, with
    references to o1 and o4.

    >>> c3 = locationCopy(o1.o3)
    >>> c3 is o1.o3
    0
    >>> c3.__parent__ is o1
    1
    >>> c3.o5 is o1.o3.o5
    0
    >>> c3.o5.__parent__ is c3
    1
    >>> c3.o4 is o1.o2.o4
    1

    """
    tmp = tempfile.TemporaryFile()
    persistent = CopyPersistent(loc)

    # Pickle the object to a temporary file
    pickler = cPickle.Pickler(tmp, 1) # XXX disable until Python 2.3.4 
    pickler.persistent_id = persistent.id
    pickler.dump(loc)

    # Now load it back
    tmp.seek(0)
    unpickler = cPickle.Unpickler(tmp)
    unpickler.persistent_load = persistent.load

    return unpickler.load()

class CopyPersistent:
    """Persistence hooks for copying locations

    See locationCopy above.

    We get initialized with an initial location:

    >>> o1 = Location()
    >>> persistent = CopyPersistent(o1)

    We provide an id function that returns None when given a non-location:

    >>> persistent.id(42)

    Or when given a location that is inside the initial location:

    >>> persistent.id(o1)
    >>> o2 = Location(); o2.__parent__ = o1
    >>> persistent.id(o2)

    But, if we get a location outside the original location, we assign
    it an id and return the id:

    >>> o3 = Location()
    >>> id3 = persistent.id(o3)
    >>> id3 is None
    0
    >>> o4 = Location()
    >>> id4 = persistent.id(o4)
    >>> id4 is None
    0
    >>> id4 is id3
    0

    If we ask for the id of an outside location more than once, we
    always get the same id back:

    >> persistent.id(o4) == id4
    1

    We also provide a load function that returns the objects for which
    we were given ids:

    >>> persistent.load(id3) is o3
    1
    >>> persistent.load(id4) is o4
    1

    """

    def __init__(self, location):
        self.location = location
        self.pids_by_id = {}
        self.others_by_pid = {}
        self.load = self.others_by_pid.get

    def id(self, object):
        if ILocation.providedBy(object):
            if not inside(object, self.location):
                if id(object) in self.pids_by_id:
                    return self.pids_by_id[id(object)]
                pid = len(self.others_by_pid)

                # The following is needed to overcome a bug
                # in pickle.py. The pickle checks the boolean value
                # if the id, rather than whether it is None.
                pid += 1
                
                self.pids_by_id[id(object)] = pid
                self.others_by_pid[pid] = object
                return pid

        return None


class PathPersistent:
    """Persistence hooks for pickling locations

    See locationCopy above.

    Unlike copy persistent, we use paths for ids of outside locations
    so that we can separate pickling and unpickling in time.  We have
    to compute paths and traverse objects to load paths, but paths can
    be stored for later use, unlike the ids used by CopyPersistent.

    We require outside locations that can be adapted to ITraversable.
    To simplify the example, we'll use a simple traversable location
    defined in zope.app.location, TLocation.

    Normally, general adapters are used to make objects traversable.

    We get initialized with an initial location:

    >>> o1 = Location()
    >>> persistent = PathPersistent(o1)

    We provide an id function that returns None when given a non-location:

    >>> persistent.id(42)

    Or when given a location that is inside the initial location:

    >>> persistent.id(o1)
    >>> o2 = Location(); o2.__parent__ = o1
    >>> persistent.id(o2)

    But, if we get a location outside the original location, we return it's
    path. To compute it's path, it must be rooted:

    >>> root = TLocation()
    >>> zope.interface.directlyProvides(root, IContainmentRoot)
    >>> o3 = TLocation(); o3.__name__ = 'o3'
    >>> o3.__parent__ = root; root.o3 = o3
    >>> persistent.id(o3)
    u'/o3'

    >>> o4 = TLocation(); o4.__name__ = 'o4'
    >>> o4.__parent__ = o3; o3.o4 = o4
    >>> persistent.id(o4)
    u'/o3/o4'


    We also provide a load function that returns objects by traversing
    given paths.  It has to find the root based on the object given to
    the constructor.  Therefore, that object must also be rooted:

    >>> o1.__parent__ = root
    >>> persistent.load(u'/o3') is o3
    1
    >>> persistent.load(u'/o3/o4') is o4
    1

    """

    def __init__(self, location):
        self.location = location

    def id(self, object):
        if ILocation.providedBy(object):
            if not inside(object, self.location):
                return LocationPhysicallyLocatable(object).getPath()

        return None

    def load(self, path):
        if path[:1] != u'/':
            raise ValueError("ZPersistent paths must be absolute", path)
        root = LocationPhysicallyLocatable(self.location).getRoot()
        return ITraverser(root).traverse(path[1:])

class ClassAndInstanceDescr(object):

    def __init__(self, *args):
        self.funcs = args

    def __get__(self, inst, cls):
        if inst is None:
            return self.funcs[1](cls)
        return self.funcs[0](inst)

class LocationProxy(ProxyBase):
    __doc__ = """Location-object proxy

    This is a non-picklable proxy that can be put around objects that
    don't implement ILocation.

    >>> l = [1, 2, 3]
    >>> p = LocationProxy(l, "Dad", "p")
    >>> p
    [1, 2, 3]
    >>> p.__parent__
    'Dad'
    >>> p.__name__
    'p'

    >>> import pickle
    >>> p2 = pickle.dumps(p)
    Traceback (most recent call last):
    ...
    TypeError: Not picklable

    Proxies should get their doc strings from the object they proxy:

    >>> p.__doc__ == l.__doc__
    True

    """

    zope.interface.implements(ILocation)

    __slots__ = '__parent__', '__name__'
    __safe_for_unpickling__ = True

    def __new__(self, ob, container=None, name=None):
        return ProxyBase.__new__(self, ob)

    def __init__(self, ob, container=None, name=None):
        ProxyBase.__init__(self, ob)
        self.__parent__ = container
        self.__name__ = name

    def __reduce__(self, proto=None):
        raise TypeError, "Not picklable"


    __doc__ = ClassAndInstanceDescr(
        lambda inst: getProxiedObject(inst).__doc__,
        lambda cls, __doc__ = __doc__: __doc__,
        )
    
    __reduce_ex__ = __reduce__

    __providedBy__ = DecoratorSpecificationDescriptor()

    __Security_checker__ = DecoratedSecurityCheckerDescriptor()


class TLocation(Location):
    """Simple traversable location used in examples."""

    zope.interface.implements(ITraverser)

    def traverse(self, path, default=None, request=None):
        o = self
        for name in path.split(u'/'):
           o = getattr(o, name)
        return o
