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

$Id: test_service.py,v 1.2 2002/12/25 14:13:32 jim Exp $
"""

import unittest
from zope.interface import Interface

from zope.exceptions import DuplicationError
from zope.testing.cleanup import CleanUp

from zope.component \
     import getServiceDefinitions, getService, getServiceManager
from zope.component.service \
     import UndefinedService, InvalidService
from zope.component.exceptions import ComponentLookupError

from zope.component import queryService

class IOne(Interface):
    pass

class ITwo(Interface):
    pass

class ServiceOne:
    __implements__ = IOne

class ServiceTwo:
    __implements__ = ITwo

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
        getServiceManager(None).defineService('one', IOne)
        c = ServiceOne()
        getServiceManager(None).provideService('one', c)

        getServiceManager(None).defineService('two', ITwo)
        d = ServiceTwo()
        getServiceManager(None).provideService('two', d)
        defs = getServiceDefinitions(None)
        defs.sort()
        self.assertEqual(defs,
            [('one', IOne), ('two', ITwo)])


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
