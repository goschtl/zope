##############################################################################
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
"""

$Id$
"""

import unittest
import pickle
from zope.interface import Interface, implements


from zope.exceptions import DuplicationError
from zope.testing.cleanup import CleanUp

from zope.component import getServiceDefinitions, getService, getServiceManager
from zope.component.service import UndefinedService, InvalidService
from zope.component.service import GlobalServiceManager, GlobalService
from zope.component.exceptions import ComponentLookupError
from zope.component import queryService
from zope.component.interfaces import IServiceService

class IOne(Interface):
    pass

class ITwo(Interface):
    pass

class ServiceOne(GlobalService):
    implements(IOne)

class ServiceTwo(GlobalService):
    implements(ITwo)

class Test(CleanUp, unittest.TestCase):

    def testNormal(self):
        getServiceManager(None).defineService('one', IOne)
        c = ServiceOne()
        getServiceManager(None).provideService('one', c)
        self.assertEqual(id(getService(None, 'one')), id(c))

    def testFailedLookup(self):
        self.assertRaises(ComponentLookupError, getService, None, 'two')
        self.assertEqual(queryService(None, 'two'), None)

    def testDup(self):
        getServiceManager(None).defineService('one', IOne)
        self.assertRaises(DuplicationError,
                          getServiceManager(None).defineService,
                          'one', ITwo)

        c = ServiceOne()
        getServiceManager(None).provideService('one', c)

        c2 = ServiceOne()
        self.assertRaises(DuplicationError,
                          getServiceManager(None).provideService,
                          'one', c2)

        self.assertEqual(id(getService(None, 'one')), id(c))


    def testUndefined(self):
        c = ServiceOne()
        self.assertRaises(UndefinedService,
                          getServiceManager(None).provideService,
                          'one', c)

    def testInvalid(self):
        getServiceManager(None).defineService('one', IOne)
        getServiceManager(None).defineService('two', ITwo)
        c = ServiceOne()
        self.assertRaises(InvalidService,
                          getServiceManager(None).provideService,
                          'two', c)

    def testGetService(self):
        # Testing looking up a service from a service manager container that
        # doesn't have a service manager.
        getServiceManager(None).defineService('one', IOne)
        c = ServiceOne()
        getServiceManager(None).provideService('one', c)
        class C: pass
        foo = C()
        self.assertEqual(id(getService(foo, 'one')), id(c))

    def testGetServiceDefinitions(self):
        # test that the service definitions are the ones we added
        sm = getServiceManager(None)
        sm.defineService('one', IOne)
        c = ServiceOne()
        sm.provideService('one', c)

        sm.defineService('two', ITwo)
        d = ServiceTwo()
        sm.provideService('two', d)
        defs = getServiceDefinitions(None)
        defs.sort()
        self.assertEqual(defs,
            [('Services', IServiceService), ('one', IOne), ('two', ITwo)])


    def testPickling(self):
        self.assertEqual(testServiceManager.__reduce__(), 'testServiceManager')
        sm = pickle.loads(pickle.dumps(testServiceManager))
        self.assert_(sm is testServiceManager)

        s2 = ServiceTwo()
        sm.defineService('2', ITwo)
        sm.provideService('2', s2)

        self.assert_(s2.__parent__ is sm)
        self.assertEqual(s2.__name__, '2')

        s = pickle.loads(pickle.dumps(s2))
        self.assert_(s is s2)
        testServiceManager._clear()


testServiceManager = GlobalServiceManager('testServiceManager', __name__)


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
