#############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Unit tests for RAM Cache.

$Id: test_RAMCache.py,v 1.1 2002/10/31 16:01:40 alga Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.Caching.tests.testICache import BaseICacheTest
from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.App.Traversing.IPhysicallyLocatable import IPhysicallyLocatable
from Zope.ContextWrapper import Wrapper
from Zope.ComponentArchitecture.GlobalAdapterService import provideAdapter
from Interface.Verify import verifyClass, verifyObject
from time import time


#############################################################################
# If your tests change any global registries, then uncomment the
# following import and include CleanUp as a base class of your
# test. It provides a setUp and tearDown that clear global data that
# has registered with the test cleanup framework.  If your class has
# its own setUp or tearDown, make sure you call the CleanUp setUp and
# tearDown from them, or the benefits of using CleanUp will be lost.
# Don't use CleanUp based tests outside the Zope package.

# from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

class Request:
    def __init__(self, dict=None):
        if dict is None:
            dict = {'foo': 1, 'bar': 2, 'baz': 3}
        self._dict = dict
    def __getitem__(self, key):
        return self._dict[key]

class Locatable:
    __implements__ = IPhysicallyLocatable

    def __init__(self, path=('a', 'b')):
        self.path = path

    def getPhysicalRoot(self):
        return self

    def getPhysicalPath(self):
        return self.path

class ObjectStub(Locatable):
    from Zope.ComponentArchitecture.IPresentation import IPresentation
    __implements__ = IPresentation, Locatable.__implements__
    request = Request()
    value = 56

class TestRAMCache(PlacelessSetup, 
                   TestCase, 
#                   BaseICacheTest,
                   ):
    
    def _Test__new(self):
        from Zope.App.Caching.RAMCache.RAMCache import RAMCache
        return RAMCache()

    def test_interface(self):
        from Zope.App.Caching.RAMCache.RAMCache import RAMCache
        from Zope.App.Caching.RAMCache.IRAMCache import IRAMCache
        from Zope.App.Caching.ICache import ICache
        from Zope.Event.ISubscriber import ISubscriber
        verifyObject(IRAMCache, RAMCache()) 
        verifyClass(ICache, RAMCache) 
        verifyClass(ISubscriber, RAMCache) 

    def test_init(self):
        from Zope.App.Caching.RAMCache.RAMCache import RAMCache
        c1 = RAMCache()
        c2 = RAMCache()
        self.assertNotEquals(c1._cacheId, c2._cacheId,
                             "The cacheId is not unique")

    def test_update(self):
        from Zope.App.Caching.RAMCache.RAMCache import RAMCache
        c = RAMCache()
        c.update(None, 1, 2, 3)
        s = c._getStorage()
        self.assertEqual(s.maxEntries, 1, "maxEntries not set")
        self.assertEqual(s.maxAge, 2, "maxAge not set")
        self.assertEqual(s.cleanupInterval, 3, "cleanupInterval not set")

    def test_cache(self):
        from Zope.App.Caching.RAMCache import RAMCache
        self.assertEqual(type(RAMCache.caches), type({}),
                         'no module level cache dictionary')

    def test_getStorage(self):
        from Zope.App.Caching.RAMCache.RAMCache import RAMCache
        c = RAMCache()
        c.maxAge = 123
        c.maxEntries = 2002
        c.cleanupInterval = 42
        storage1 = c._getStorage()
        storage2 = c._getStorage()
        self.assertEqual(storage1, storage2,
                         "_getStorage returns different storages")

        self.assertEqual(storage1.maxAge, 123, "maxAge not set")
        self.assertEqual(storage1.maxEntries, 2002, "maxEntries not set")
        self.assertEqual(storage1.cleanupInterval, 42,
                         "cleanupInterval not set")

    def test_buildKey(self): 
        from Zope.App.Caching.RAMCache.RAMCache import RAMCache

        r = Request()
        key = RAMCache._buildKey('view', r, ('foo', 'bar'), {'baz': 42})

        self.assertEqual(key, ('view', ('foo', 1, 'bar', 2), (('baz', 42),)),
                         "wrong key")

        key = RAMCache._buildKey('view', r, ('frob', 'bar'), {'baz': 42})

        self.assertEqual(key, ('view', ('bar', 2), (('baz', 42),)),
                         "wrong key")

    def test_query(self):
        from Zope.App.Caching.RAMCache.RAMCache import RAMCache

        location = ('aaa',)
        ob = Locatable(path=location)
        
        keywords = {"answer": 42}
        value = "true"
        c = RAMCache()
        c.requestVars = ('foo', 'bar')
        key = RAMCache._buildKey('', None, None, keywords)
        c._getStorage().setEntry(location, key, value)

        self.assertEqual(c.query(ob, '', keywords=keywords), value,
                         "incorrect value")

        self.assertEqual(c.query(ob, ''), None, "defaults incorrect")
        self.assertEqual(c.query(ob, '', keywords={"answer": 2}, default="bummer"),
                         "bummer", "default doesn't work")

        ob = ObjectStub(path=location)
        key = RAMCache._buildKey('', ob.request, ('foo', 'bar'), keywords)
        c._getStorage().setEntry(location, key, ob.value)
        
        self.assertEqual(c.query(ob, '', keywords), ob.value)
        

    def test_set(self):
        from Zope.App.Caching.RAMCache.RAMCache import RAMCache

        location = ('path',)
        ob = Locatable(path=location)
        keywords = {"answer": 42}
        value = "true"
        c = RAMCache()
        c.requestVars = ('foo', 'bar')
        key = RAMCache._buildKey('', None, None, keywords)

        c.set(value, ob, keywords=keywords)
        self.assertEqual(c._getStorage().getEntry(location, key), value,
                         "Not stored correctly")

        ob = ObjectStub(path=location)
        key = RAMCache._buildKey('view', ob.request, ('foo', 'bar'), keywords)
        c.set(ob.value, ob, 'view', keywords)

        self.assertEqual(c._getStorage().getEntry(location, key), ob.value)
        
    def test_invalidate(self):
        from Zope.App.Caching.RAMCache.RAMCache import RAMCache

        location1 = ("loc1",)
        location2 = ("loc2",)
        ob1 = Locatable(path=location1)
        ob2 = Locatable(path=location2)
        keywords = {"answer": 42}
        keywords2 = {"answer": 41}
        value = "true"
        c = RAMCache()
        key1 = RAMCache._buildKey('v', None, None, keywords)
        key2 = RAMCache._buildKey('v', None, None, keywords)
        key3 = RAMCache._buildKey('V', None, None, keywords2)

        # Test deleting entries with the view and keywords passed
        c._getStorage().setEntry(location1, key1, value)
        c._getStorage().setEntry(location2, key2, value)
        c._getStorage().setEntry(location2, key3, value)

        c.invalidate(ob1, 'v', keywords)

        self.assertRaises(KeyError, c._getStorage().getEntry, location1, key1)
        c._getStorage().getEntry(location2, key2)
        c._getStorage().getEntry(location2, key3)

        # Test deleting a view for an object
        c._getStorage().setEntry(location1, key1, value)
        c._getStorage().setEntry(location2, key2, value)
        c._getStorage().setEntry(location2, key3, value)

        c.invalidate(ob2, 'V')
        c._getStorage().getEntry(location1, key1)
        c._getStorage().getEntry(location2, key2)
        self.assertRaises(KeyError, c._getStorage().getEntry, location2, key3)
        
        # Test deleting the whole object
        c._getStorage().setEntry(location1, key1, value)
        c._getStorage().setEntry(location2, key2, value)
        c._getStorage().setEntry(location2, key3, value)

        c.invalidate(ob2)
        self.assertRaises(KeyError, c._getStorage().getEntry, location2, key2)
        self.assertRaises(KeyError, c._getStorage().getEntry, location2, key3)
        c._getStorage().getEntry(location1, key1)
        
        # Try something that's not there
        c.invalidate(Locatable())

    def test_notify(self):
        from Zope.App.Caching.RAMCache.RAMCache import RAMCache
        from Zope.Event.ObjectEvent import ObjectModifiedEvent

        location = ('aaa',)
        ob = Locatable(path=location)
        
        keywords = {"answer": 42}
        value = "true"
        c = RAMCache()
        key = RAMCache._buildKey('', None, None, keywords)
        c._getStorage().setEntry(location, key, value)

        event = ObjectModifiedEvent(ob, location)

        c.notify(event)

        self.assertRaises(KeyError, c._getStorage().getEntry, location, key)


class TestStorage(TestCase):
        
    def test_getEntry(self):
        from Zope.App.Caching.RAMCache.RAMCache import Storage
        s = Storage()
        object = 'object'
        key = ('view', (), ('answer', 42))
        value = 'yes'
        timestamp = time()
        
        s._data = {object: {key: [value, timestamp, 1]}}
        self.assertEqual(s.getEntry(object, key), value, 'got wrong value')
        
        self.assert_(s._data[object][key][2] == 2, 'access count not updated')

    def test_setEntry(self):
        from Zope.App.Caching.RAMCache.RAMCache import Storage
        
        s = Storage(cleanupInterval=300, maxAge=300)
        object = 'object'
        key = ('view', (), ('answer', 42))
        key2 = ('view2', (), ('answer', 42))
        value = 'yes'

        t1 = time()
        s.setEntry(object, key, value)
        t2 = time()

        timestamp = s._data[object][key][1]
        self.failUnless(t1 <= timestamp <= t2, 'wrong timestamp')
        
        self.assertEqual(s._data, {object: {key: [value, timestamp, 0]}},
                         'stored data incorrectly')

        s._data[object][key][1] = time() - 400
        s.lastCleanup = time() - 400

        s.setEntry(object, key2, value)

        timestamp = s._data[object][key2][1]
        self.assertEqual(s._data, {object: {key2: [value, timestamp, 0]}},
                         'cleanup not called')
        

    def test_set_get(self):
        from Zope.App.Caching.RAMCache.RAMCache import Storage
        s = Storage()
        object = 'object'
        key = ('view', (), ('answer', 42))
        value = 'yes'
        s.setEntry(object, key, value)
        self.assertEqual(s.getEntry(object, key), value,
                         'got something other than set')

    def test_do_invalidate(self):
        from Zope.App.Caching.RAMCache.RAMCache import Storage
        s = Storage()
        object = 'object'
        object2 = 'object2'
        key = ('view', (), ('answer', 41))
        key2 = ('view2', (), ('answer', 42))
        value = 'yes'
        ts = time()
        s._data = {object:  {key: [value, ts, 0],
                             key2: [value, ts, 0]},
                   object2: {key: [value, ts, 0]}}
        s._do_invalidate(object)
        self.assertEqual(s._data, {object2: {key: [value, ts, 0]}},
                         'invalidation failed')

        s._data = {object:  {key: [value, ts, 0],
                             key2: [value, ts, 0]},
                   object2: {key: [value, ts, 0]}}
        s._do_invalidate(object, key2)
        self.assertEqual(s._data,
                         {object:  {key: [value, ts, 0]},
                          object2: {key: [value, ts, 0]}},
                         'invalidation of one key failed')

    def test_invalidate(self):
        from Zope.App.Caching.RAMCache.RAMCache import Storage
        s = Storage()
        object = 'object'
        object2 = 'object2'
        key = ('view', (), ('answer', 41))
        key2 = ('view2', (), ('answer', 42))
        value = 'yes'
        ts = time()
        s._data = {object:  {key: [value, ts, 0],
                             key2: [value, ts, 0]},
                   object2: {key: [value, ts, 0]}}
        
        s.writelock.acquire()
        try:
            s.invalidate(object)
        finally:
            s.writelock.release()
        self.assertEqual(s._invalidate_queue, [(object, None)],
                         "nothing in the invalidation queue")

        s._data = {object:  {key: [value, ts, 0],
                             key2: [value, ts, 0]},
                   object2: {key: [value, ts, 0]}}
        s.invalidate(object)
        self.assertEqual(s._data, {object2: {key: [value, ts, 0]}},
                         "not invalidated")
        
    def test_invalidate_queued(self):
        from Zope.App.Caching.RAMCache.RAMCache import Storage
        s = Storage()
        object = 'object'
        object2 = 'object2'
        object3 = 'object3'
        key = ('view', (), ('answer', 41))
        key2 = ('view2', (), ('answer', 42))
        value = 'yes'
        ts = time()
        s._data = {object:  {key: [value, ts, 0],
                             key2: [value, ts, 0]},
                   object2: {key: [value, ts, 0]},
                   object3: "foo" }
        s._invalidate_queue = [(object2, None), (object3, None)]
        s._invalidate_queued()
        self.assertEqual(s._data,
                         {object: {key: [value, ts, 0], key2: [value, ts, 0]}},
                         "failed to invalidate queued")

    def test_getKeys(self):
        from Zope.App.Caching.RAMCache.RAMCache import Storage
        s = Storage()
        object = 'object'
        object2 = 'object2'
        key = ('view', (), ('answer', 41))
        key2 = ('view2', (), ('answer', 42))
        value = 'yes'
        ts = time()
        s._data = {object:  {key: [value, ts, 0],
                             key2: [value, ts, 0]},
                   object2: {key: [value, ts, 0]}}
        keys = s.getKeys(object)
        expected = [key, key2]
        keys.sort()
        expected.sort()
        self.assertEqual(keys, expected, 'bad keys')


    def test_removeStale(self):
        from Zope.App.Caching.RAMCache.RAMCache import Storage
        s = Storage(maxAge=100)
        object = 'object'
        object2 = 'object2'
        key = ('view', (), ('answer', 42))
        value = 'yes'
        timestamp = time()
        s._data = {object:  {key: [value, timestamp-101, 2]},
                   object2: {key: [value, timestamp-90, 0]}}
        s.removeStaleEntries()
        self.assertEqual(s._data, {object2: {key: [value, timestamp-90, 0]}},
                         'stale records removed incorrectly')

        
        s = Storage(maxAge=0)
        s._data = {object:  {key: [value, timestamp, 2]},
                   object2: {key: [value, timestamp-90, 0]}}
        d = s._data.copy()
        s.removeStaleEntries()
        self.assertEqual(s._data, d,
                         'records removed when maxAge == 0')

    def test_locking(self):
        from Zope.App.Caching.RAMCache.RAMCache import Storage
        s = Storage(maxAge=100)
        s.writelock.acquire()
        try:
            self.assert_(s.writelock.locked(), "locks don't work")
        finally:
            s.writelock.release()

    def test_removeLeastAccessed(self):
        from Zope.App.Caching.RAMCache.RAMCache import Storage
        s = Storage(maxEntries=3)
        object = 'object'
        object2 = 'object2'
        key1 = ('view1', (), ('answer', 42))
        key2 = ('view2', (), ('answer', 42))
        key3 = ('view3', (), ('answer', 42))
        value = 'yes'
        timestamp = time()
        s._data = {object:  {key1: [value, 1, 10],
                             key2: [value, 2, 5],
                             key3: [value, 3, 2]},
                   object2: {key1: [value, 4, 2],
                             key2: [value, 5, 1],
                             key3: [value, 6, 1]}}
        s.removeLeastAccessed()
        self.assertEqual(s._data,
                         {object:  {key1: [value, 1, 0],
                                    key2: [value, 2, 0]}},
                         'least records removed incorrectly')

        s = Storage(maxEntries=6)
        s._data = {object:  {key1: [value, timestamp, 10],
                             key2: [value, timestamp, 5],
                             key3: [value, timestamp, 2]},
                   object2: {key1: [value, timestamp, 2],
                             key2: [value, timestamp, 1],
                             key3: [value, timestamp, 1]}}
        c = s._data.copy()
        s.removeLeastAccessed()
        self.assertEqual(s._data, c, "modified list even though len < max")

    def test__clearAccessCounters(self):
        from Zope.App.Caching.RAMCache.RAMCache import Storage
        s = Storage(maxEntries=3)
        object = 'object'
        object2 = 'object2'
        key1 = ('view1', (), ('answer', 42))
        key2 = ('view2', (), ('answer', 42))
        key3 = ('view3', (), ('answer', 42))
        value = 'yes'
        timestamp = time()
        s._data = {object:  {key1: [value, 1, 10],
                             key2: [value, 2, 5],
                             key3: [value, 3, 2]},
                   object2: {key1: [value, 4, 2],
                             key2: [value, 5, 1],
                             key3: [value, 6, 1]}}

        cleared = {object:  {key1: [value, 1, 0],
                             key2: [value, 2, 0],
                             key3: [value, 3, 0]},
                   object2: {key1: [value, 4, 0],
                             key2: [value, 5, 0],
                             key3: [value, 6, 0]}}

        s._clearAccessCounters()
        self.assertEqual(s._data, cleared, "access counters not cleared")


class TestModule(TestCase):

    def test_locking(self):
        from Zope.App.Caching.RAMCache.RAMCache import writelock
        writelock.acquire()
        try:
            self.failUnless(writelock.locked(), "locks don't work")
        finally:
            writelock.release()
    
#############################################################################

class Test(TestCase):
    pass

def test_suite():
    return TestSuite((
        makeSuite(TestRAMCache),
        makeSuite(TestStorage),
        makeSuite(TestModule),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
