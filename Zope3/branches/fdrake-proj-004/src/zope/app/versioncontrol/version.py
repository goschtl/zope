##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Version Implementation

$Id$
"""
import tempfile
import time
from cStringIO import StringIO
from cPickle import Pickler, Unpickler

import persistent

from BTrees.OOBTree import OOBTree

import zope.app.location

from zope.app.versioncontrol.interfaces import VersionControlError
from zope.app.versioncontrol.interfaces import INonVersionedData


def cloneByPickle(obj, ignore_list=()):
    """Makes a copy of a ZODB object, loading ghosts as needed.

    Ignores specified objects along the way, replacing them with None
    in the copy.
    """
    ignore_dict = {}
    for o in ignore_list:
        ignore_dict[id(o)] = o
    ids = {"ignored": object()}

    def persistent_id(ob):
        if ignore_dict.has_key(id(ob)):
            return 'ignored'
        if (zope.app.location.ILocation.providedBy(object)
            and not zope.app.location.inside(ob, obj)):
            myid = id(ob)
            ids[myid] = ob
            return myid
        if getattr(ob, '_p_changed', 0) is None:
            ob._p_changed = 0
        return None

    stream = StringIO()
    p = Pickler(stream, 1)
    p.persistent_id = persistent_id
    p.dump(obj)
    stream.seek(0)
    u = Unpickler(stream)
    u.persistent_load = ids.get
    return u.load()


class Version(persistent.Persistent, zope.app.location.Location):
    """A Version is a resource that contains a copy of a particular state
    (content and dead properties) of a version-controlled resource.  A
    version is created by checking in a checked-out resource. The state
    of a version of a version-controlled resource never changes."""

    def __init__(self, version_id):
        self.__name__ = version_id
        self.date_created = time.time()
        self._data = None

    # These attributes are set by the createVersion method of the version
    # history at the time the version is created. The branch is the name
    # of the branch on which the version was created. The prev attribute
    # is the version id of the predecessor to this version. The next attr
    # is a sequence of version ids of the successors to this version.
    branch = 'mainline'
    prev = None
    next = ()

    def saveState(self, obj):
        """Save the state of `obj` as the state for this version of
           a version-controlled resource."""
        self._data = self.stateCopy(obj)

    def copyState(self):
        """Return an independent deep copy of the state of the version."""
        return self.stateCopy(self._data)

    def stateCopy(self, obj):
        """Get a deep copy of the state of an object.

        Breaks any database identity references.
        """
        ignore = INonVersionedData(obj).listNonVersionedObjects()
        res = cloneByPickle(obj, ignore)
        INonVersionedData(res).removeNonVersionedData()
        return res
