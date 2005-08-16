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
Locking adapter implementation.

$Id: $
"""

from zope.app.locking.interfaces import ILockable, ILockedEvent
from zope.app.locking.interfaces import IUnlockedEvent, IBreakLockEvent
from zope.app.keyreference.interfaces import IKeyReference
from zope.component.exceptions import ComponentLookupError
from zope.app.event.objectevent import ObjectEvent
from zope.app.locking.interfaces import LockingError
from zope.app.locking.storage import ILockStorage
from zope.app.locking.lockinfo import LockInfo
from zope.app.locking.interfaces import _
from zope.component import getUtility
import zope.security.management
from zope.event import notify
import zope.interface



def LockingAdapterFactory(target):
    """
    Return target adapted to ILockable, or None. This should be registered
    against zope.interface.Interface to provide adaptation to ILockable.
    """
    if IKeyReference(target, None) is None:
        return None
    return LockingAdapter(target)
    

class LockingAdapter(object):
    """
    Default ILockable adapter implementation.
    """

    zope.interface.implements(ILockable)
    
    def __init__(self, context):
        try:
            self.storage = getUtility(ILockStorage, context=context)
        except ComponentLookupError:
            self.storage = getUtility(ILockStorage)
        self.context = context

    def _findPrincipal(self):
        # Find the current principal. Note that it is possible for there
        # to be more than one principal - in this case we throw an error.
        interaction = zope.security.management.getInteraction()
        principal = None
        for p in interaction.participations:
            if principal is None:
                principal = p.principal
            else:
                raise LockingError(_("Multiple principals found"))
        if principal is None:
            raise LockingError(_("No principal found"))
        return principal

    def lock(self, principal=None, timeout=None):
        if principal is None:
            principal = self._findPrincipal()
        principal_id = principal.id
        lock = self.storage.getLock(self.context)
        if lock is not None:
            raise LockingError(_("Object is already locked"))
        lock = LockInfo(self.context, principal_id, timeout)
        self.storage.setLock(self.context, lock)
        notify(LockedEvent(self.context, lock))
        return lock

    def unlock(self):
        lock = self.storage.getLock(self.context)
        if lock is None:
            raise LockingError(_("Object is not locked"))
        principal = self._findPrincipal()
        if lock.principal_id != principal.id:
            raise LockingError(_("Principal is not lock owner"))
        self.storage.delLock(self.context)
        notify(UnlockedEvent(self.context))

    def breaklock(self):
        lock = self.storage.getLock(self.context)
        if lock is None:
            raise LockingError(_("Object is not locked"))
        self.storage.delLock(self.context)
        notify(BreakLockEvent(self.context))

    def locked(self):
        lock = self.storage.getLock(self.context)
        return lock is not None

    def locker(self):
        lock = self.storage.getLock(self.context)
        if lock is not None:
            return lock.principal_id
        return None

    def getLockInfo(self):
        return self.storage.getLock(self.context)

    def ownLock(self):
        lock = self.storage.getLock(self.context)
        if lock is not None:
            principal = self._findPrincipal()
            return lock.principal_id == principal.id
        return False

    def isLockedOut(self):
        lock = self.storage.getLock(self.context)
        if lock is not None:
            principal = self._findPrincipal()
            return lock.principal_id != principal.id
        return False

    def __repr__(self):
        return '<Locking adapter for %s>' % repr(self.context)



class EventBase(ObjectEvent):
    def __repr__(self):
        return '%s for %s' % (self.__class__.__name__, `self.object`)

class LockedEvent(EventBase):
    zope.interface.implements(ILockedEvent)

    def __init__(self, object, lock):
        self.object = object
        self.lock = lock


class UnlockedEvent(EventBase):
    zope.interface.implements(IUnlockedEvent)

class BreakLockEvent(UnlockedEvent):
    zope.interface.implements(IBreakLockEvent)


class LockingPathAdapter(object):

    zope.interface.implements(
        zope.app.traversing.interfaces.IPathAdapter)

    def __init__(self, target):
        self._locking = LockingAdapterFactory(target)
        self.lockable = self._locking is not None

    def lockedOut(self):
        return (self._locking is not None) and self._locking.isLockedOut()
    lockedOut = property(lockedOut)

    def locked(self):
        return (self._locking is not None) and self._locking.locked()
    locked = property(locked)

    def ownLock(self):
        return (self._locking is not None) and self._locking.ownLock()
    ownLock = property(ownLock)
