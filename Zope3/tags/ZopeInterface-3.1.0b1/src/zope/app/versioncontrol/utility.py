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
"""Version Control Utilities

$Id$
"""
import time
from cStringIO import StringIO
from cPickle import Pickler

import persistent

from ZODB.serialize import referencesf
from ZODB.TimeStamp import TimeStamp

import zope.security.management

import zope.app.versioncontrol.interfaces


def isAVersionableResource(obj):
    """ True if an object is versionable.

    To qualify, the object must be persistent (have its own db record), and
    must not have an true attribute named '__non_versionable__'.
    """
    return zope.app.versioncontrol.interfaces.IVersionable.providedBy(obj)


class VersionInfo(persistent.Persistent):
    """Container for bookkeeping information.

    The bookkeeping information can be read (but not changed) by
    restricted code.
    """

    def __init__(self, history_id, version_id, status):
        self.history_id = history_id
        self.version_id = version_id
        self.status = status
        self.touch()

    sticky = None

    def branchName(self):
        if self.sticky is not None and self.sticky[0] == 'B':
            return self.sticky[1]
        return 'mainline'

    def touch(self):
        self.user_id = _findUserId()
        self.timestamp = time.time()


def _findUserId():
    interaction = zope.security.management.getInteraction()
    return interaction.participations[0].principal.id

def _findModificationTime(object):
    """Find the last modification time for a version-controlled object.
       The modification time reflects the latest modification time of
       the object or any of its persistent subobjects that are not
       themselves version-controlled objects. Note that this will
       return None if the object has no modification time."""

    serial = [object._p_serial]

    def persistent_id(ob):
        s = getattr(ob, '_p_serial', None)
        if not isinstance(s, str):
            return None

        # XXX obviously no test for this
        if (zope.app.location.ILocation.providedBy(ob)
            and not zope.app.location.inside(ob, object)):
            return '1' # go away

#          The location check above should wake the object
##         if getattr(ob, '_p_changed', 0) is None:
##             ob._p_changed = 0

        serial[0] = max(serial[0], s)
        
        return None

    stream = StringIO()
    p = Pickler(stream, 1)
    p.persistent_id = persistent_id
    p.dump(object)

    return serial[0]
