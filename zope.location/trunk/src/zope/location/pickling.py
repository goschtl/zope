##############################################################################
#
# Copyright (c) 2003-2009 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Location copying/pickling support

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.component import adapts
from zope.copy.interfaces import ICopyHook, ResumeCopy
from zope.deferredimport import deprecated
from zope.interface import implements

import zope.location.interfaces
from zope.location.location import inside
from zope.location.traversing import LocationPhysicallyLocatable

class LocationCopyHook(object):
    """Copy hook to preserve copying referenced objects that are not
    located inside object that's being copied.

    To see the problem, imagine we want to copy an ILocation object that
    contains an attribute-based reference to another ILocation object
    and the referenced object is not contained inside object being copied. 
    
    Without this hook, the referenced object will be cloned:
    
    >>> from zope.location.location import Location, locate
    >>> root = Location()
    >>> page = Location()
    >>> locate(page, root, 'page')
    >>> image = Location()
    >>> locate(page, root, 'image')
    >>> page.thumbnail = image
    
    >>> from zope.copy import copy
    >>> page_copy = copy(page)
    >>> page_copy.thumbnail is image
    False

    But if we will provide a hook, the attribute will point to the
    original object as we might want.

    >>> from zope.component import provideAdapter
    >>> provideAdapter(LocationCopyHook)

    >>> from zope.copy import copy
    >>> page_copy = copy(page)
    >>> page_copy.thumbnail is image
    True
    
    """
    
    adapts(zope.location.interfaces.ILocation)
    implements(ICopyHook)
    
    def __init__(self, context):
        self.context = context
    
    def __call__(self, toplevel, register):
        if not inside(self.context, toplevel):
            return self.context
        raise ResumeCopy
        
# BBB 2009/02/09
deprecated(
    'The locationCopy was replaced by more generic "clone" function'
    'in the zope.copy package. This reference may be removed someday.',
    locationCopy='zope.copy:clone'
    )
deprecated(
    'The CopyPersistent was made more generic and moved to the'
    'zope.copy package. This reference may be removed someday.',
    CopyPersistent='zope.copy:CopyPersistent',
)

# XXX: is this actually used anywhere? (nadako, 2009/02/09)
class PathPersistent(object):
    """Persistence hooks for pickling locations

    See `locationCopy` above.

    Unlike copy persistent, we use paths for ids of outside locations
    so that we can separate pickling and unpickling in time.  We have
    to compute paths and traverse objects to load paths, but paths can
    be stored for later use, unlike the ids used by `CopyPersistent`.

    We require outside locations that can be adapted to `ITraversable`.
    To simplify the example, we'll use a simple traversable location
    defined in `zope.location.tests`, `TLocation`.

    Normally, general adapters are used to make objects traversable.

    We get initialized with an initial location:

    >>> from zope.location.location import Location
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

    >>> from zope.location.tests import TLocation
    >>> from zope.interface import directlyProvides
    >>> root = TLocation()
    >>> directlyProvides(root, zope.location.interfaces.IRoot)
    >>> o3 = TLocation()
    >>> o3.__name__ = 'o3'
    >>> o3.__parent__ = root
    >>> root.o3 = o3
    >>> persistent.id(o3)
    u'/o3'

    >>> o4 = TLocation()
    >>> o4.__name__ = 'o4'
    >>> o4.__parent__ = o3
    >>> o3.o4 = o4
    >>> persistent.id(o4)
    u'/o3/o4'

    We also provide a load method that returns objects by traversing
    given paths.  It has to find the root based on the object given to
    the constructor.  Therefore, that object must also be rooted:

    >>> o1.__parent__ = root
    >>> persistent.load(u'/o3') is o3
    True
    >>> persistent.load(u'/o3/o4') is o4
    True

    We must provide an absolute path for the load method:

    >>> persistent.load(u'o3')
    Traceback (most recent call last):
    ...
    ValueError: ('Persistent paths must be absolute', u'o3')

    """

    def __init__(self, location):
        self.location = location

    def id(self, object):
        if zope.location.interfaces.ILocation.providedBy(object):
            if not inside(object, self.location):
                return LocationPhysicallyLocatable(object).getPath()
        return None

    def load(self, path):
        if not path.startswith(u'/'):
            raise ValueError("Persistent paths must be absolute", path)
        root = LocationPhysicallyLocatable(self.location).getRoot()
        return zope.location.interfaces.ITraverser(root).traverse(path[1:])
