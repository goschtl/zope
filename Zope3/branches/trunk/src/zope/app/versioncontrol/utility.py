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

    mtime = getattr(object, '_p_serial', None)
    if mtime is None:
        return None

    latest = mtime
    conn = object._p_jar
    load = conn._storage.load
    version = conn._version
    refs = referencesf

    oids=[object._p_oid]
    done_oids={}
    done=done_oids.has_key
    first = True

    while oids:
        oid=oids[0]
        del oids[0]
        if done(oid):
            continue
        done_oids[oid]=1
        try: p, serial = load(oid, version)
        except: pass # invalid reference!
        else:
            if first:
                first = False
            else:
                if p.find('U\x0b__vc_info__') == -1:
                    if serial > latest:
                        latest = serial
            refs(p, oids)

    return latest
