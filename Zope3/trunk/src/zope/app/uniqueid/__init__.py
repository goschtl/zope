##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
Unique id utility.

This utility assigns unique integer ids to objects and allows lookups
by object and by id.

This functionality can be used in cataloging.

$Id$
"""
import random
from zope.app.uniqueid.interfaces import IUniqueIdUtility, IReference
from zope.interface import implements
from ZODB.interfaces import IConnection
from BTrees import OIBTree, IOBTree
from zope.app import zapi
from zope.app.location.interfaces import ILocation
from zope.security.proxy import trustedRemoveSecurityProxy

class UniqueIdUtility:
    """This utility provides a two way mapping between objects and
    integer ids.

    IReferences to objects are stored in the indexes.
    """
    implements(IUniqueIdUtility, ILocation)

    __parent__ = None
    __name__ = None

    def __init__(self):
        self.ids = OIBTree.OIBTree()
        self.refs = IOBTree.IOBTree()

    def __len__(self):
        return len(self.ids)

    def items(self):
        return list(self.refs.items())

    def getObject(self, id):
        return self.refs[id]()

    def getId(self, ob):
        ref = zapi.getAdapter(ob, IReference)
        return self.ids[ref]

    def _generateId(self):
        while True:
            uid = random.randint(0, 2**31)
            if uid not in self.refs:
                return uid

    def register(self, ob):
        ob = trustedRemoveSecurityProxy(ob)
        ref = zapi.getAdapter(ob, IReference)
        if ref in self.ids:
            return self.ids[ref]
        uid = self._generateId()
        self.refs[uid] = ref
        self.ids[ref] = uid
        return uid

    def unregister(self, ob):
        ref = zapi.getAdapter(ob, IReference)
        uid = self.ids[ref]
        del self.refs[uid]
        del self.ids[ref]


class ReferenceToPersistent:
    """An IReference for persistent object which is comparable.

    These references compare by _p_oids of the objects they reference.
    """
    implements(IReference)

    def __init__(self, object):
        self.object = object
        if not getattr(object, '_p_oid', None):
            zapi.getAdapter(object, IConnection).add(object)

    def __call__(self):
        return self.object

    def __hash__(self):
        return self.object._p_oid

    def __cmp__(self, other):
        if not isinstance(other, ReferenceToPersistent):
            raise TypeError("Cannot compare ReferenceToPersistent with %r" %
                            (other,))
        return cmp(self.__hash__(), other.__hash__())


def connectionOfPersistent(ob):
    """An adapter which gets a ZODB connection of a persistent object.

    We are assuming the object has a parent if it has been created in
    this transaction.

    Raises ValueError if it is impossible to get a connection.
    """
    cur = ob
    while not getattr(cur, '_p_jar', None):
        cur = getattr(cur, '__parent__', None)
        if cur is None:
            raise ValueError('Can not get connection of %r' % (ob,))
    return cur._p_jar
