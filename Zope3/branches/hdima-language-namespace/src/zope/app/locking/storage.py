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

import time

import persistent

from BTrees.OOBTree import OOBTree
from BTrees.IOBTree import IOBTree

import zope.component
import zope.interface

from zope.app.keyreference.interfaces import IKeyReference
from zope.app.locking.interfaces import ILockTracker
from zope.app.locking.interfaces import LockingError
from zope.app.size.interfaces import ISized

from zope.app.i18n import ZopeMessageIDFactory as _


timefunc = time.time


class ILockStorage(zope.interface.Interface):
    """
    This interface is internal to the default locking implementation. It
    lets us store lock information in a central place rather than store
    it on individual objects.
    """


class LockStorage(object):
    # WARNING: This is not persistent.  Use PersistentLockStorage instead.
    # This class must remain so that existing instances can be unpickled
    # from the database.  New instances cannot be created without subclassing.
    #
    # The persistent.Persistent base class cannot be added to this
    # without causing the containers to fail to unpickle properly
    # since the pickle for a LockStorage is embedded in the pickle of
    # the containing object.  For this reason, applications must
    # replace existing LockStorage instances with some new class.  The
    # LockStorage instances don't need to be removed, but an alternate
    # class needs to be used instead.

    """Peristent storage for locks.

    This class implements both the ILockTracker utility as well as the
    internal ILockStorage utility which is used by the ILockable adapter
    implementation. It acts as the persistent storage for locks.

    """

    zope.interface.implements(ILockStorage, ILockTracker)
    
    def __init__(self):
        self.timeouts = IOBTree()
        self.locks = OOBTree()
        if self.__class__ is LockStorage:
            raise TypeError(
                "%s.LockStorage is insane; use a persistent subclass instead"
                " (%s.PersistentLockStorage should do nicely)"
                % (__name__, __name__))

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


class Sized(object):

    zope.interface.implements(ISized)
    zope.component.adapts(ILockStorage)

    def __init__(self, context):
        self.context = context

    def sizeForSorting(self):
        return ('item', self._get_size())

    def sizeForDisplay(self):
        num_items = self._get_size()
        if num_items == 1:
            return _('1 item')
        size = _('${items} items')
        size.mapping = {'items': str(num_items)}
        return size

    def _get_size(self):
        # We only want to include active locks, so we'd like to simply
        # call `cleanup()`, but we also don't want to cause the
        # transaction to write, so we adjust the count instead.

        nlocks = len(self.context.locks)
        for key in self.context.timeouts.keys(max=int(timefunc())):
            for keyref in self.context.timeouts[key]:
                if self.context.locks.get(keyref, None) is not None:
                    nlocks -= 1
        return nlocks


class PersistentLockStorage(persistent.Persistent, LockStorage):
    """LockStorage that isn't fickle."""

    # This is the class that should generally be used with Zope 3.
    # Alternate subclasses can be used, but LockStorage can't be used
    # directly.  Subclasses are responsible for providing persistence.
