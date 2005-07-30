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
Locking interfaces

$Id: $
"""

from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.event.interfaces import IObjectEvent
from zope.interface import Interface, Attribute
from zope.i18nmessageid import MessageIDFactory
from zope.interface.common.mapping import IMapping
import zope.interface
import zope.schema

_ = MessageIDFactory('zope.app.locking')


class ILockable(Interface):
    """
    The ILockable interface defines the locking operations that are
    supported for lockable objects.
    """

    def lock(timeout=None):
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
        Break all existing locks on an object for all principals.
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

    def getLockInfo(obj):
        """
        Return a (possibly empty) sequence of ILockInfo objects describing
        the current locks on the object.
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


class ILockTracker(Interface):
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

    def getObject():
        """Return the actual locked object."""

    creator = zope.schema.TextLine(
        description=_("id of the principal owning the lock")
        )

    created = zope.schema.Float(
        description=_("time value indicating the creation time"),
        required=False
        )

    timeout = zope.schema.Float(
        description=_("time value indicating the lock timeout from creation"),
        required=False
        )



class ILockedEvent(IObjectEvent):
    """An object has been locked"""

    lock = Attribute("The lock set on the object")
    
class IUnlockedEvent(IObjectEvent):
    """An object has been unlocked"""

class IBreakLockEvent(IUnlockedEvent):
    """Lock has been broken on an object"""



class LockingError(Exception):
    """
    The exception raised for locking errors.
    """

