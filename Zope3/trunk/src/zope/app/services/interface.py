##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Interfaces for persistent modules."""

from persistence import Persistent, PersistentMetaClass
from zodb.code.patch import registerWrapper, Wrapper
from zope.interface.interface import InterfaceClass

class PersistentInterfaceClass(Persistent, InterfaceClass):
    pass

# PersistentInterface is equivalent to the zope.interface.Interface object
# except that it is also persistent.  It is used in conjunction with
# zodb.code to support interfaces in persistent modules.
PersistentInterface = PersistentInterfaceClass("PersistentInterface")

class PersistentInterfaceWrapper(Wrapper):

    def unwrap(self, bases, dict):
        pi = PersistentInterfaceClass(self._obj.__name__, bases, {})
        pi.__dict__.update(dict)
        return pi

registerWrapper(InterfaceClass, PersistentInterfaceWrapper,
                lambda iface: (iface.__bases__, iface.__dict__))
