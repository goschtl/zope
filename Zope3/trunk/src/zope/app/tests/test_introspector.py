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
from zope.interface import Interface, Attribute

class ITestClass(Interface):
    def drool():
        """...drool..."""

class BaseTestClass:
    """This is stupid base class"""
    pass

class TestClass(BaseTestClass):
    """This is my stupid doc string"""
    __implements__ = ITestClass
    def drool(self):
        pass

class I(Interface):
    """bah blah"""

class I2(I):
    """eek"""

class I3(I, I2):
    """This is dummy doc string"""

    testAttribute1 = Attribute("""This is a dummy attribute.""")
    testAttribute2 = Attribute("""This is a dummy attribute.""")

    def one(param):
        """method one"""

    def two(param1, param2):
        """method two"""


"""

Revision information:
$Id: test_introspector.py,v 1.2 2002/12/25 14:13:26 jim Exp $
"""

from zope.interface import Interface
from unittest import TestCase, TestSuite, main, makeSuite
from zope.testing.cleanup import CleanUp
from zope.app.introspector import Introspector



class Test(CleanUp, TestCase):
    """Test Introspector."""

    def testIntrospector(self):
        # Testing introspector
        ints = Introspector(ITestClass)
        self.assertEqual(ints.isInterface(), 1)

        ints = Introspector(TestClass())
        self.assertEqual(ints.isInterface(), 0)
        request = {}
        ints.setRequest(request)
        self.assertEqual(ints.getClass(), 'TestClass')

        ints = Introspector(TestClass)
        self.assertEqual(ints.isInterface(), 0)
        request['PATH_INFO'] = (
            '++module++zope.app.tests.test_introspector.TestClass')
        ints.setRequest(request)
        self.assertEqual(ints.getClass(), 'TestClass')
        self.assertEqual(
            ints.getBaseClassNames(),
            ['zope.app.tests.test_introspector.BaseTestClass'])
        self.assertEqual(
            ints.getModule(),
            'zope.app.tests.test_introspector')
        self.assertEqual(ints.getDocString(), "This is my stupid doc string")
        self.assertEqual(ints.getInterfaces(), (ITestClass,))
        self.assertEqual(
            ints.getInterfaceNames(),
            ['zope.app.tests.test_introspector.ITestClass'])
        self.assertEqual(ints.getExtends(), (BaseTestClass,))

        ints = Introspector(I3)
        self.assertEqual(ints.isInterface(), 1)
        request['PATH_INFO'] = (
            '++module++zope.app.tests.test_introspector.I3')
        ints.setRequest(request)
        self.assertEqual(
            ints.getModule(),
            'zope.app.tests.test_introspector')
        self.assertEqual(ints.getExtends(), (I, I2, ))
        self.assertEqual(
            ints.getDocString(),
            "This is dummy doc string")
        Iname = 'I3'
        bases = ['zope.app.tests.test_introspector.I',
                 'zope.app.tests.test_introspector.I2']
        desc = 'This is dummy doc string'
        m1_name = 'one'
        m1_signature = '(param)'
        m1_desc = 'method one'
        m2_name = 'two'
        m2_signature = '(param1, param2)'
        m2_desc = 'method two'
        methods = [(m1_name, m1_signature, m1_desc),
                   (m2_name, m2_signature, m2_desc),]
        attr_name1 = 'testAttribute1'
        attr_desc1 = 'This is a dummy attribute.'
        attr_name2 = 'testAttribute2'
        attr_desc2 = 'This is a dummy attribute.'
        attributes = [(attr_name1, attr_desc1),
                      (attr_name2, attr_desc2), ]
        details = [Iname, bases, desc, methods, attributes]
        self.assertEqual(ints.getInterfaceDetails(), details)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(Test))
    return suite


if __name__ == '__main__':
    main(defaultTest='test_suite')
