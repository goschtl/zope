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

$Id$
"""

from zope import interface, component, event
import zope.security.management
from zope.app.keyreference.interfaces import IKeyReference
from zope.i18nmessageid import ZopeMessageFactory as _

from zope.app.locking.lockinfo import LockInfo
from zope.app.locking import interfaces

@component.adapter(interface.Interface)
@interface.implementer(interfaces.ILockable)
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

    # this MUST be a trusted adapter!!

    interface.implements(interfaces.ILockable)

    def __init__(self, context):
        self.storage = component.getUtility(interfaces.ILockStorage)
        self.context = context
        self.__parent__ = context

    def _findPrincipal(self):
        # Find the current principal. Note that it is possible for there
        # to be more than one principal - in this case we throw an error.
        interaction = zope.security.management.getInteraction()
        principal = None
        for p in interaction.participations:
            if principal is None:
                principal = p.principal
            else:
                raise interfaces.LockingError(_("Multiple principals found"))
        if principal is None:
            raise interfaces.LockingError(_("No principal found"))
        return principal

    def lock(self, timeout=None, principal=None):
        if principal is None:
            principal = self._findPrincipal()
        principal_id = principal.id
        lock = self.storage.getLock(self.context)
        if lock is not None:
            raise interfaces.LockingError(_("Object is already locked"))
        lock = LockInfo(self.context, principal_id, timeout)
        self.storage.setLock(self.context, lock)
        event.notify(interfaces.LockedEvent(self.context, lock))
        return lock

    def unlock(self):
        lock = self.storage.getLock(self.context)
        if lock is None:
            raise interfaces.LockingError(_("Object is not locked"))
        principal = self._findPrincipal()
        if lock.principal_id != principal.id:
            raise interfaces.LockingError(_("Principal is not lock owner"))
        self.storage.delLock(self.context)
        event.notify(interfaces.UnlockedEvent(self.context))

    def breaklock(self):
        lock = self.storage.getLock(self.context)
        if lock is None:
            raise interfaces.LockingError(_("Object is not locked"))
        self.storage.delLock(self.context)
        event.notify(interfaces.BreakLockEvent(self.context))

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

class LockingPathAdapter(object):
    interface.implements(zope.traversing.interfaces.IPathAdapter)

    def __init__(self, target):
        self._locking = LockingAdapterFactory(target)
        self.lockable = self._locking is not None

    @property
    def lockedOut(self):
        return (self._locking is not None) and self._locking.isLockedOut()

    @property
    def locked(self):
        return (self._locking is not None) and self._locking.locked()

    @property
    def ownLock(self):
        return (self._locking is not None) and self._locking.ownLock()
