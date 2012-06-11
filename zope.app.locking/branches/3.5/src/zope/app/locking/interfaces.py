##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
Locking interfaces

$Id$
"""
from zope import interface, schema

from zope.component.interfaces import ObjectEvent, IObjectEvent
from zope.interface.common.mapping import IMapping
from zope.i18nmessageid import ZopeMessageFactory as _

class ILockable(interface.Interface):
    """
    The ILockable interface defines the locking operations that are
    supported for lockable objects.
    """

    def lock(principal=None, timeout=None):
        """
        Lock the object in the name of the current principal. This method
        raises a LockingError if the object cannot be locked by the current
        principal.
        """

    def unlock():
        """
        Unlock the object. If the current principal does not hold a lock
        on the object, this method raises a LockingError.
        """

    def breaklock():
        """
        Break the lock on the object, regardless of whether the current
        principal created the lock.  Raises a LockingError if there is not a
        lock on the object
        """

    def locked():
        """
        Returns true if the object is locked.
        """

    def locker():
        """
        Return the principal id of the principal that owns the lock on
        the object, or None if the object is not locked.
        """

    def getLockInfo():
        """
        Return an ILockInfo describing the current lock or None.
        """

    def ownLock():
        """
        Returns true if the object is locked by the current principal.
        """

    def isLockedOut():
        """
        Returns true if the object is locked by a principal other than
        the current principal.
        """


class ILockTracker(interface.Interface):
    """
    An ILockTracker implementation is responsible for tracking what
    objects are locked within its scope.
    """

    def getLocksForPrincipal(principal_id):
        """
        Return a sequence of all locks held by the given principal.
        """

    def getAllLocks():
        """
        Return a sequence of all currently held locks.
        """


class ILockInfo(IMapping):
    """
    An ILockInfo implementation is responsible for 
    """

    target = interface.Attribute("""the actual locked object.""")

    principal_id = schema.TextLine(
        description=_("id of the principal owning the lock")
        )

    created = schema.Float(
        description=_("time value indicating the creation time"),
        required=False
        )

    timeout = schema.Float(
        description=_("time value indicating the lock timeout from creation"),
        required=False
        )

class ILockStorage(interface.Interface):
    """
    A lock storage lets you store information about locks in a central place
    """

    def getLock(object):
        """
        Get the current lock for an object.
        """

    def setLock(object, lock):
        """
        Set the current lock for an object.
        """

    def delLock(object):
        """
        Delete the current lock for an object.
        """

    def cleanup():
        """We occasionally want to clean up expired locks to keep them
        from accumulating over time and slowing things down.
        """

# event interfaces

class ILockedEvent(IObjectEvent):
    """An object has been locked"""

    lock = interface.Attribute("The lock set on the object")

class IUnlockedEvent(IObjectEvent):
    """An object has been unlocked"""

class IBreakLockEvent(IUnlockedEvent):
    """Lock has been broken on an object"""

# events

class EventBase(ObjectEvent):
    def __repr__(self):
        return '%s for %s' % (self.__class__.__name__, `self.object`)

class LockedEvent(EventBase):
    interface.implements(ILockedEvent)

    def __init__(self, object, lock):
        self.object = object
        self.lock = lock


class UnlockedEvent(EventBase):
    interface.implements(IUnlockedEvent)

class BreakLockEvent(UnlockedEvent):
    interface.implements(IBreakLockEvent)

# exceptions

class LockingError(Exception):
    """
    The exception raised for locking errors.
    """

