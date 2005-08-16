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
Tests for the unique id utility.

$Id$
"""
import unittest
from zope.interface.verify import verifyObject
from persistent import Persistent
from persistent.interfaces import IPersistent
from zope.app.tests import setup, ztapi
from zope.app import zapi
from zope.interface import implements
from ZODB.interfaces import IConnection
from zope.app.location.interfaces import ILocation
from zope.app.component.hooks import setSite
from zope.app.utility import LocalUtilityService
from zope.app.servicenames import Utilities


class P(Persistent):
    implements(ILocation)


class ConnectionStub:
    next = 1
    def add(self, ob):
        ob._p_jar = self
        ob._p_oid = self.next
        self.next += 1


class ReferenceSetupMixin:
    """Registers adapters ILocation->IConnection and IPersistent->IReference"""
    def setUp(self):
        from zope.app.uniqueid import connectionOfPersistent
        from zope.app.uniqueid import ReferenceToPersistent
        from zope.app.uniqueid.interfaces import IReference
        self.root = setup.placefulSetUp(site=True)
        ztapi.provideAdapter(ILocation, IConnection, connectionOfPersistent)
        ztapi.provideAdapter(IPersistent, IReference, ReferenceToPersistent)

    def tearDown(self):
        setup.placefulTearDown()


class TestUniqueIdUtility(ReferenceSetupMixin, unittest.TestCase):

    def test_interface(self):
        from zope.app.uniqueid.interfaces import IUniqueIdUtility
        from zope.app.uniqueid import UniqueIdUtility

        verifyObject(IUniqueIdUtility, UniqueIdUtility())

    def test(self):
        from zope.app.uniqueid import UniqueIdUtility

        u = UniqueIdUtility()
        obj = P()
        obj._p_jar = ConnectionStub()

        uid = u.register(obj)
        self.assert_(u.getObject(uid) is obj)
        self.assertEquals(u.getId(obj), uid)

        uid2 = u.register(obj)
        self.assertEquals(uid, uid2)

        u.unregister(obj)
        self.assertRaises(KeyError, u.getObject, uid)
        self.assertRaises(KeyError, u.getId, obj)

    def test_len_items(self):
        from zope.app.uniqueid import UniqueIdUtility
        from zope.app.uniqueid import ReferenceToPersistent
        u = UniqueIdUtility()
        obj = P()
        obj._p_jar = ConnectionStub()

        self.assertEquals(len(u), 0)
        self.assertEquals(u.items(), [])

        uid = u.register(obj)
        ref = ReferenceToPersistent(obj)
        self.assertEquals(len(u), 1)
        self.assertEquals(u.items(), [(uid, ref)])

        obj2 = P()
        obj2.__parent__ = obj

        uid2 = u.register(obj2)
        ref2 = ReferenceToPersistent(obj2)
        self.assertEquals(len(u), 2)
        result = u.items()
        expected = [(uid, ref), (uid2, ref2)]
        result.sort()
        expected.sort()
        self.assertEquals(result, expected)

        u.unregister(obj)
        u.unregister(obj2)
        self.assertEquals(len(u), 0)
        self.assertEquals(u.items(), [])

    def test_getenrateId(self):
        from zope.app.uniqueid import UniqueIdUtility

        u = UniqueIdUtility()
        self.assertEquals(u._v_nextid, None)
        id1 = u._generateId()
        self.assert_(u._v_nextid is not None)
        id2 = u._generateId()
        self.assert_(id1 + 1, id2)
        u.refs[id2 + 1] = "Taken"
        id3 = u._generateId()
        self.assertNotEqual(id3, id2 + 1)
        self.assertNotEqual(id3, id2)
        self.assertNotEqual(id3, id1)


class TestReferenceToPersistent(ReferenceSetupMixin, unittest.TestCase):

    def test(self):
        from zope.app.uniqueid.interfaces import IReference
        from zope.app.uniqueid import ReferenceToPersistent

        ob = P()
        ob._p_oid = 'x' * 20
        ref = ReferenceToPersistent(ob)
        verifyObject(IReference, ref)
        self.assert_(ref() is ob)

        parent = P()
        conn = ConnectionStub()
        parent._p_jar = conn
        ob2 = P()
        ob2.__parent__ = parent
        ref = ReferenceToPersistent(ob2)
        ob = ref()
        self.assert_(ob is ob2)
        self.assertEquals(ob._p_jar, conn)

    def test_compare(self):
        from zope.app.uniqueid import ReferenceToPersistent

        ob1 = Persistent()
        ob2 = Persistent()
        ob3 = Persistent()
        ob1._p_oid = 'x' * 20
        ob2._p_oid = ob3._p_oid = 'y' * 20
        ref1 = ReferenceToPersistent(ob1)
        ref2 = ReferenceToPersistent(ob2)
        ref3 = ReferenceToPersistent(ob3)
        self.assert_(ref1 < ref2)
        self.assert_(ref2 == ref3)
        self.assertRaises(TypeError, ref1.__cmp__, object())


class TestConnectionOfPersistent(unittest.TestCase):

    def test(self):
        from zope.app.uniqueid import connectionOfPersistent

        conn = object()

        ob1 = P()
        ob1._p_jar = conn

        ob2 = P()
        ob2.__parent__ = ob1

        ob3 = P()

        self.assertEquals(connectionOfPersistent(ob1), conn)
        self.assertEquals(connectionOfPersistent(ob2), conn)
        self.assertRaises(ValueError, connectionOfPersistent, ob3)

        ob3.__parent__ = object()
        self.assertRaises(ValueError, connectionOfPersistent, ob3)
        self.assertRaises(ValueError, connectionOfPersistent, object())


class TestRemoveSubscriber(ReferenceSetupMixin, unittest.TestCase):

    def setUp(self):
        from zope.app.uniqueid.interfaces import IUniqueIdUtility
        from zope.app.uniqueid import UniqueIdUtility
        from zope.app.folder import Folder, rootFolder

        ReferenceSetupMixin.setUp(self)

        sm = zapi.getServices(self.root)
        setup.addService(sm, Utilities, LocalUtilityService())
        self.utility = setup.addUtility(sm, '1',
                                        IUniqueIdUtility, UniqueIdUtility())

        self.root['folder1'] = Folder()
        self.root._p_jar = ConnectionStub()
        self.root['folder1']['folder1_1'] = self.folder1_1 = Folder()
        self.root['folder1']['folder1_1']['folder1_1_1'] = Folder()

        sm1_1 = setup.createServiceManager(self.folder1_1)
        setup.addService(sm1_1, Utilities, LocalUtilityService())
        self.utility1 = setup.addUtility(sm1_1, '2', IUniqueIdUtility,
                                         UniqueIdUtility())

    def test(self):
        from zope.app.uniqueid import removeUniqueIdSubscriber
        from zope.app.container.contained import ObjectRemovedEvent
        from zope.app.uniqueid.interfaces import IUniqueIdRemovedEvent
        folder = self.root['folder1']['folder1_1']['folder1_1_1']
        id = self.utility.register(folder)
        id1 = self.utility1.register(folder)
        self.assertEquals(self.utility.getObject(id), folder)
        self.assertEquals(self.utility1.getObject(id1), folder)
        setSite(self.folder1_1)

        events = []
        ztapi.handle([IUniqueIdRemovedEvent], events.append)

        # This should unregister the object in all utilities, not just the
        # nearest one.
        removeUniqueIdSubscriber(ObjectRemovedEvent(folder))

        self.assertRaises(KeyError, self.utility.getObject, id)
        self.assertRaises(KeyError, self.utility1.getObject, id1)

        self.assertEquals(len(events), 1)
        self.assertEquals(events[0].original_event.object, folder)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestUniqueIdUtility))
    suite.addTest(unittest.makeSuite(TestReferenceToPersistent))
    suite.addTest(unittest.makeSuite(TestConnectionOfPersistent))
    suite.addTest(unittest.makeSuite(TestRemoveSubscriber))
    return suite

if __name__ == '__main__':
    unittest.main()
