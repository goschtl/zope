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
"""Unique id utility.

This utility assigns unique integer ids to objects and allows lookups
by object and by id.

This functionality can be used in cataloging.

$Id$
"""
import random

from BTrees import OIBTree, IOBTree
from persistent import Persistent
from ZODB.interfaces import IConnection

from zope.app.container.contained import Contained
from zope.app.uniqueid.interfaces import IUniqueIdUtility, IReference
from zope.app.uniqueid.interfaces import UniqueIdRemovedEvent
from zope.interface import implements
from zope.app import zapi
from zope.security.proxy import trustedRemoveSecurityProxy
from zope.event import notify


class UniqueIdUtility(Persistent, Contained):
    """This utility provides a two way mapping between objects and
    integer ids.

    IReferences to objects are stored in the indexes.
    """
    implements(IUniqueIdUtility)

    _v_nextid = None

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
        ref = IReference(ob)
        return self.ids[ref]

    def _generateId(self):
        """Generate an id which is not yet taken.

        This tries to allocate sequential ids so they fall into the
        same BTree bucket, and randomizes if it stumbles upon a
        used one.
        """
        while True:
            if self._v_nextid is None:
                self._v_nextid = random.randint(0, 2**31)
            uid = self._v_nextid
            self._v_nextid += 1
            if uid not in self.refs:
                return uid
            self._v_nextid = None

    def register(self, ob):
        ob = trustedRemoveSecurityProxy(ob)
        ref = IReference(ob)
        if ref in self.ids:
            return self.ids[ref]
        uid = self._generateId()
        self.refs[uid] = ref
        self.ids[ref] = uid
        return uid

    def unregister(self, ob):
        ref = IReference(ob)
        uid = self.ids[ref]
        del self.refs[uid]
        del self.ids[ref]


class ReferenceToPersistent(object):
    """An IReference for persistent object which is comparable.

    These references compare by _p_oids of the objects they reference.
    """
    implements(IReference)

    def __init__(self, object):
        self.object = object
        if not getattr(object, '_p_oid', None):
            IConnection(object).add(object)

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


def removeUniqueIdSubscriber(event):
    """A subscriber to ObjectRemovedEvent

    Removes the unique ids registered for the object in all the unique
    id utilities.
    """

    # Notify the catalogs that this object is about to be removed.
    notify(UniqueIdRemovedEvent(event))

    for utility in zapi.getAllUtilitiesRegisteredFor(IUniqueIdUtility):
        try:
            utility.unregister(event.object)
        except KeyError:
            pass

