##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
from zope.interface import Interface
from unittest import TestCase, TestSuite, main, makeSuite
from zope.testing.cleanup import CleanUp
from zope.app.interfaces.component import IGlobalDAVSchemaService
from zope.app.dav.globaldavschemaservice import DAVSchemaService
from zope.interface.verify import verifyObject
from zope.component.exceptions import ComponentLookupError

class B(Interface):
    pass

class I(Interface):
    """bah blah
    """

class I2(B):
    """eek
    """

class I3(B):
    """
    """
    def one():
        """method one"""

    def two():
        """method two"""

class Test(CleanUp, TestCase):
    """Test Interface for DAVSchemaService Instance.
    """

    def testInterfaceVerification(self):

        verifyObject(IGlobalDAVSchemaService, DAVSchemaService())

    def testInterfaceService(self):
        service = DAVSchemaService()

        self.assertRaises(ComponentLookupError,
                          service.getInterface, 'http://www.foo.bar/boxschema/')
        self.assertEqual(service.queryInterface('http://www.foo.bar/boxschema/'), None)
        self.assertEqual(service.queryInterface('http://www.foo.bar/boxschema/', 42), 42)
        self.failIf(service.searchInterface(''))

        service.provideInterface('http://www.foo.bar/boxschema/', I)

        self.assertEqual(service.getInterface('http://www.foo.bar/boxschema/'), I)
        self.assertEqual(service.queryInterface('http://www.foo.bar/boxschema/'), I)
        self.assertEqual(list(service.searchInterface('')), [I])
        self.assertEqual(list(service.searchInterface(base=B)), [])

        service.provideInterface('http://www.foo.bag/boxschema/', I2)

        result = list(service.searchInterface(''))
        result.sort()
        self.assertEqual(result, [I, I2])

        self.assertEqual(list(service.searchInterface('I2')), [I2])
        self.assertEqual(list(service.searchInterface('eek')), [I2])

        self.assertEqual(list(service.searchInterfaceIds('I2')), ['http://www.foo.bag/boxschema/'])
        self.assertEqual(list(service.searchInterfaceIds('eek')), ['http://www.foo.bag/boxschema/'])

        service.provideInterface('http://www.foo.baz/boxschema/', I3)
        self.assertEqual(list(service.searchInterface('two')), [I3])
        self.assertEqual(list(service.searchInterface('two', base=B)), [I3])

        r = list(service.searchInterface(base=B))
        r.sort()
        self.assertEqual(r, [I2, I3])

def test_suite():
    return TestSuite((makeSuite(Test),))

if __name__=='__main__':
    main(defaultTest='test_suite')
    self.assertEqual(list(service.searchInterface('two')), [I3])


def test_suite():
    return TestSuite((makeSuite(Test),))

if __name__=='__main__':
    main(defaultTest='test_suite')
