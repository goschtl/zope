##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""
Locking tests

$Id$
"""
import sys, unittest, time
from zope.component.testing import PlacelessSetup
import zope.event
from zope.testing import doctest
from transaction import abort

from zope.interface import Interface
from zope.traversing.interfaces import IPathAdapter
from zope.security.testing import Principal, Participation
from zope.site.folder import Folder

from zope.app.testing import ztapi, setup
from zope.app.file.file import File
from zope.app.locking.interfaces import ILockable, ILockTracker
from zope.app.locking.adapter import LockingAdapterFactory
from zope.app.locking.adapter import LockingPathAdapter
from zope.app.locking.storage import ILockStorage, PersistentLockStorage
from zope.app.keyreference.interfaces import IKeyReference

class FakeModule:
    def __init__(self, dict):
        self.__dict = dict
    def __getattr__(self, name):
        try:
            return self.__dict[name]
        except KeyError:
            raise AttributeError(name)

name = 'zope.app.locking.README'

ps = PlacelessSetup()


from zope.app.keyreference.interfaces import IKeyReference

class FakeKeyReference(object):
    """Fake keyref for testing"""
    def __init__(self, object):
        self.object = object

    def __call__(self):
        return self.object

    def __hash__(self):
        return id(self.object)

    def __cmp__(self, other):
        return cmp(id(self.object), id(other.object))

def maybeFakeKeyReference(ob):
    if not isinstance(ob, int):
        return FakeKeyReference(ob)

class TestLockStorage(unittest.TestCase):

    def setUp(self):
        super(TestLockStorage, self).setUp()
        setup.placelessSetUp()
        zope.security.management.endInteraction()

        ztapi.provideAdapter(Interface, IKeyReference, FakeKeyReference)
        ztapi.provideAdapter(Interface, ILockable, LockingAdapterFactory)
        ztapi.provideAdapter(None, IPathAdapter, LockingPathAdapter,
                             "locking")

        self.storage = storage = PersistentLockStorage()
        ztapi.provideUtility(ILockStorage, storage)
        ztapi.provideUtility(ILockTracker, storage)

    def tearDown(self):
        super(TestLockStorage, self).tearDown()
        del self.storage
        setup.placelessTearDown()

    def test_timeout(self):
        # fake time function to avoid a time.sleep in tests
        def faketime(t):
            zope.app.locking.storage.timefunc = lambda : t

        ## test the cleanup of timedout locks.
        content = File('some content', 'text/plain')
        lockable = ILockable(content)
        participation = Participation(Principal('michael'))
        zope.security.management.newInteraction(participation)
        now = time.time()
        faketime(now)
        lockinfo = lockable.lock(timeout = 1)
        lockinfo.created = now
        # two seconds pass
        faketime(now + 2.0)
        ## now lockable.locked is False since the lock has timed out
        self.assertEqual(lockable.locked(), False)
        ## since lockable.locked is False lockable.lock should succeed
        ## assume this is done 3 seconds after the first lock
        lockinfo = lockable.lock(timeout = 20)
        lockinfo.created = now + 3.0
        faketime(now + 4.0) # let time pass
        self.assertEqual(lockable.locked(), True)
        zope.security.management.endInteraction()
        # reset the time function
        zope.app.locking.storage.timefunc = time.time

    def test_folder_lock(self):
        folder = Folder()
        file = File('some content', 'text/plain')
        folder['file'] = file

        participation = Participation(Principal('michael'))
        zope.security.management.newInteraction(participation)

        lockablefolder = ILockable(folder)
        lockablefolder.lock()
        self.assertEqual(lockablefolder.locked(), True)
        lockablefile = ILockable(folder['file'])
        self.assertEqual(lockablefile.locked(), False)

        zope.security.management.endInteraction()

def setUp(test):
    ps.setUp()
    dict = test.globs
    dict.clear()
    dict['__name__'] = name
    sys.modules[name] = FakeModule(dict)

    ztapi.provideAdapter(Interface, IKeyReference, maybeFakeKeyReference)
    ztapi.provideAdapter(Interface, ILockable, LockingAdapterFactory)
    ztapi.provideAdapter(None, IPathAdapter, LockingPathAdapter,
                         "locking")
    storage = PersistentLockStorage()
    ztapi.provideUtility(ILockStorage, storage)
    ztapi.provideUtility(ILockTracker, storage)
    test._storage = storage # keep-alive


def tearDown(test):
    import zope.app.locking.storage
    import time
    del sys.modules[name]
    abort()
    db = test.globs.get('db')
    if db is not None:
        db.close()
    ps.tearDown()
    del test._storage
    zope.event.subscribers.pop()
    zope.app.locking.storage.timefunc = time.time


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite('README.txt', setUp=setUp,
                                       tearDown=tearDown,
                                       optionflags=(doctest.ELLIPSIS)
                                       ))
    suite.addTest(unittest.makeSuite(TestLockStorage))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
