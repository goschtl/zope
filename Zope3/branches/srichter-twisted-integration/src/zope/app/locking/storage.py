##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""
Lock storage implementation.

$Id: $
"""

from zope.app.keyreference.interfaces import IKeyReference
from zope.app.locking.interfaces import ILockTracker
from zope.app.locking.interfaces import LockingError
from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree
import zope.interface, time


timefunc = time.time


class ILockStorage(zope.interface.Interface):
    """
    This interface is internal to the default locking implementation. It
    lets us store lock information in a central place rather than store
    it on individual objects.
    """


class LockStorage(object):
    """
    This class implements both the ILockTracker utility as well as the
    internal ILockStorage utility which is used by the ILockable adapter
    implementation. It acts as the persistent storage for locks.
    """

    zope.interface.implements(ILockStorage, ILockTracker)
    
    def __init__(self):
        self.timeouts = IOBTree()
        self.locks = OOBTree()

    # ILockTracker implementation
    
    def getLocksForPrincipal(self, principal_id):
        return self.currentLocks(principal_id)

    def getAllLocks(self):
        return self.currentLocks()

    # ILockStorage implementation

    def currentLocks(self, principal_id=None):
        """
        Return the currently active locks, possibly filtered by principal.
        """
        result = []
        for lock in self.locks.values():
            if principal_id is None or principal_id == lock.principal_id:
                if (lock.timeout is None or 
                   (lock.created + lock.timeout > timefunc())
                    ):
                    result.append(lock)
        return result
                    
    def getLock(self, object):
        """
        Get the current lock for an object.
        """
        keyref = IKeyReference(object)
        lock = self.locks.get(keyref, None)
        if lock is not None and lock.timeout is not None:
            if lock.created + lock.timeout < timefunc():
                return None
        return lock

    def setLock(self, object, lock):
        """
        Set the current lock for an object.
        """
        keyref = IKeyReference(object)
        self.locks[keyref] = lock
        pid = lock.principal_id
        if lock.timeout:
            ts = int(lock.created + lock.timeout)
            value = self.timeouts.get(ts, [])
            value.append(keyref)
            self.timeouts[ts] = value
        self.cleanup()

    def delLock(self, object):
        """
        Delete the current lock for an object.
        """
        keyref = IKeyReference(object)
        del self.locks[keyref]

    def cleanup(self):
        # We occasionally want to clean up expired locks to keep them
        # from accumulating over time and slowing things down. 
        for key in self.timeouts.keys(max=int(timefunc())):
            for keyref in self.timeouts[key]:
                if self.locks.get(keyref, None) is not None:
                    del self.locks[keyref]
            del self.timeouts[key]

        

