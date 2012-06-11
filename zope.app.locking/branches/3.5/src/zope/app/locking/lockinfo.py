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
ILockInfo implementation.

$Id$
"""
import time
import persistent.mapping
import zope.interface
from zope.app.locking.interfaces import ILockInfo

class LockInfo(persistent.mapping.PersistentMapping):

    zope.interface.implements(ILockInfo)

    def __init__(self, target, principal_id, timeout=None):
        # must not store target with security proxy.
        super(LockInfo, self).__init__()
        self.__parent__ = self.target = target
        self.principal_id = principal_id
        self.created = time.time()
        self.timeout = timeout

    def __repr__(self):
        return "<%s.%s object at 0x%x>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            id(self))
