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

$Id:$
"""

import sys, unittest
from zope.component.tests.placelesssetup import PlacelessSetup
import zope.event
from zope.testing import doctest
from transaction import abort


class FakeModule:
    def __init__(self, dict):
        self.__dict = dict
    def __getattr__(self, name):
        try:
            return self.__dict[name]
        except KeyError:
            raise AttributeError, name

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



def setUp(test):
    ps.setUp()
    dict = test.globs
    dict.clear()
    dict['__name__'] = name    
    sys.modules[name] = FakeModule(dict)

    from zope.app.testing import ztapi
    from zope.interface import Interface
    from zope.app.locking.interfaces import ILockable, ILockTracker
    from zope.app.locking.adapter import LockingAdapterFactory
    from zope.app.locking.adapter import LockingPathAdapter
    from zope.app.locking.storage import ILockStorage, LockStorage
    from zope.app.traversing.interfaces import IPathAdapter

    ztapi.provideAdapter(Interface, IKeyReference, FakeKeyReference)
    ztapi.provideAdapter(Interface, ILockable, LockingAdapterFactory)
    ztapi.provideAdapter(None, IPathAdapter, LockingPathAdapter,
                         "locking")
    storage = LockStorage()
    ztapi.provideUtility(ILockStorage, storage)
    ztapi.provideUtility(ILockTracker, storage)
    test._storage = storage # keep-alive


def tearDown(test):
    del sys.modules[name]
    abort()
    db = test.globs.get('db')
    if db is not None:
        db.close()
    ps.tearDown()
    del test._storage
    zope.event.subscribers.pop()

def test_suite():
    return doctest.DocFileSuite('README.txt', setUp=setUp, tearDown=tearDown,
                                optionflags=(doctest.ELLIPSIS)
                                )


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
