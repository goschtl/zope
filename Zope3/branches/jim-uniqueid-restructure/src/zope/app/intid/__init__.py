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
from BTrees import IOBTree, OIBTree
from ZODB.interfaces import IConnection
from persistent import Persistent

from zope.event import notify
from zope.interface import implements
from zope.security.proxy import removeSecurityProxy

from zope.app import zapi

from zope.app.container.contained import Contained
from zope.app.keyreference.interfaces import IKeyReference
from zope.app.location.interfaces import ILocation

from zope.app.intid.interfaces import IIntIds
from zope.app.intid.interfaces import IntIdRemovedEvent
from zope.app.intid.interfaces import IntIdAddedEvent

class IntIds(Persistent, Contained):
    """This utility provides a two way mapping between objects and
    integer ids.

    IKeyReferences to objects are stored in the indexes.
    """
    implements(IIntIds)

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

    def queryObject(self, id, default=None):
        r = self.refs.get(id)
        if r is not None:
            return r()
        return default

    def getId(self, ob):
        ref = IKeyReference(ob)
        return self.ids[ref]

    def queryId(self, ob, default=None):
        ref = IKeyReference(ob)
        return self.ids.get(ref, default)

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
        # Note that we'll still need to keep this proxy removal.
        ob = removeSecurityProxy(ob)
        ref = IKeyReference(ob)
        if ref in self.ids:
            return self.ids[ref]
        uid = self._generateId()
        self.refs[uid] = ref
        self.ids[ref] = uid
        return uid

    def unregister(self, ob):
        ref = IKeyReference(ob)
        uid = self.ids[ref]
        del self.refs[uid]
        del self.ids[ref]

def removeIntIdSubscriber(ob, event):
    """A subscriber to ObjectRemovedEvent

    Removes the unique ids registered for the object in all the unique
    id utilities.
    """

    # Notify the catalogs that this object is about to be removed.
    notify(IntIdRemovedEvent(ob, event))

    for utility in zapi.getAllUtilitiesRegisteredFor(IIntIds):
        try:
            utility.unregister(ob)
        except KeyError:
            pass

def addIntIdSubscriber(ob, event):
    """A subscriber to ObjectAddedEvent

    Registers the object added in all unique id utilities and fires
    an event for the catalogs.
    """
    for utility in zapi.getAllUtilitiesRegisteredFor(IIntIds):
        utility.register(ob)

    notify(IntIdAddedEvent(ob, event))

# BBB
UniqueIdUtility = IntIds
import zope.app.keyreference
ReferenceToPersistent = zope.app.keyreference.KeyReferenceToPersistent
import sys
sys.modules['zope.app.uniqueid'] = sys.modules['zope.app.intid']
del sys
