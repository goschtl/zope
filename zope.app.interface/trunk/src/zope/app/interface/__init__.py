##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Code about interfaces.

This module contains code for interfaces in persistent modules.

$Id$
"""
__docformat__ = 'restructuredtext'


from persistent import Persistent
from zodbcode.patch import registerWrapper, Wrapper, NameFinder
from zope.interface.interface import InterfaceClass
from zope.interface import Interface
from wref import FlexibleWeakKeyDictionary

# BBB import
from zope.app.content import queryType


class PersistentInterfaceClass(Persistent, InterfaceClass):

    def __init__(self, *args, **kw):
        Persistent.__init__(self)
        InterfaceClass.__init__(self, *args, **kw)

        self.dependents = FlexibleWeakKeyDictionary()

    def __hash__(self):
        # Override the version in InterfaceClass to cope with the fact that
        # we don't have __module__
        return hash((self._p_jar, self._p_oid))

    def __eq__(self, other):
        # Override the version in InterfaceClass to cope with the fact that
        # we don't have __module__
        if self._p_oid is None:
            return other is self
        return (self._p_jar is getattr(other, '_p_jar', None) and
                self._p_oid == getattr(other, '_p_oid', None))

    def __ne__(self, other):
        # Override the version in InterfaceClass to cope with the fact that
        # we don't have __module__
        if self._p_oid is None:
            return other is not self
        return (self._p_jar is not getattr(other, '_p_jar', None) or
                self._p_oid != getattr(other, '_p_oid', None))

# PersistentInterface is equivalent to the zope.interface.Interface object
# except that it is also persistent.  It is used in conjunction with
# zodb.code to support interfaces in persistent modules.
PersistentInterface = PersistentInterfaceClass("PersistentInterface",
                                               (Interface, ))


class PersistentInterfaceWrapper(Wrapper):

    def unwrap(self):
        return PersistentInterfaceClass(self._obj.__name__)


def getInterfaceStateForPersistentInterfaceCreation(iface):
    # Need to convert the dependents weakref dict to a persistent dict
    dict = iface.__dict__.copy()
    dependents = FlexibleWeakKeyDictionary()
    for k, v in dict['dependents'].iteritems():
        dependents[k] = v
    dict['dependents'] = dependents
    return dict

registerWrapper(InterfaceClass, PersistentInterfaceWrapper,
                lambda iface: (),
                getInterfaceStateForPersistentInterfaceCreation,
                )

NameFinder.classTypes[InterfaceClass] = True
NameFinder.types[InterfaceClass] = True
NameFinder.classTypes[PersistentInterfaceClass] = True
NameFinder.types[PersistentInterfaceClass] = True


