##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Factory-related Tests

$Id$
"""
import unittest
from zope.interface import Interface, implements

from zope import component as capi
from zope.component.interfaces import IFactory
from zope.component.factory import Factory
from zope.component.tests.placelesssetup import setUp, tearDown
from zope.testing import doctest

class IFunction(Interface):
    pass

class IKlass(Interface):
    pass

class Klass(object):
    implements(IKlass)

    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw

factory = Factory(Klass, 'Klass', 'Klassier')
factory2 = Factory(lambda x: x, 'Func', 'Function')
factory3 = Factory(lambda x: x, 'Func', 'Function', (IFunction,))

def testFactoryCall():
    """Here we test whether the factory correctly creates the objects and
    including the correct handling of constructor elements.

    First we create a factory that creates instanace of the `Klass` class:

      >>> factory = Factory(Klass, 'Klass', 'Klassier')

    Now we use the factory to create the instance
    
      >>> kl = factory(1, 2, foo=3, bar=4)

    and make sure that the correct class was used to create the object:
    
      >>> kl.__class__
      <>

    Since we passed in one 
      
      >>> kl.args
      (3, )
      >>> kl.kw
      {'foo': 4}
      
      >>> factory2(3)
      3
      >>> factory3(3)
      3
    """

def testTitleDescription(self):
    self.assertEqual(self._factory.title, 'Klass')
    self.assertEqual(self._factory.description, 'Klassier')
    self.assertEqual(self._factory2.title, 'Func')
    self.assertEqual(self._factory2.description, 'Function')
    self.assertEqual(self._factory3.title, 'Func')
    self.assertEqual(self._factory3.description, 'Function')

def testGetInterfaces(self):
    implemented = self._factory.getInterfaces()
    self.assert_(implemented.isOrExtends(IKlass))
    self.assertEqual(list(implemented), [IKlass])
    self.assertEqual(implemented.__name__,
                     'zope.component.tests.test_factory.Klass')

    implemented2 = self._factory2.getInterfaces()
    self.assertEqual(list(implemented2), [])
    self.assertEqual(implemented2.__name__, '<lambda>')

    implemented3 = self._factory3.getInterfaces()
    self.assertEqual(list(implemented3), [IFunction])
    self.assertEqual(implemented3.__name__, '<lambda>')


class TestFactoryZAPIFunctions(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TestFactoryZAPIFunctions, self).setUp()
        self.factory = Factory(Klass, 'Klass', 'Klassier')
        gsm = capi.getGlobalSiteManager() 
        gsm.registerUtility(IFactory, self.factory, 'klass')

    def testCreateObject(self):
        kl = capi.createObject(None, 'klass', 3, foo=4)
        self.assert_(isinstance(kl, Klass))
        self.assertEqual(kl.args, (3, ))
        self.assertEqual(kl.kw, {'foo': 4})

    def testGetFactoryInterfaces(self):
        implemented = capi.getFactoryInterfaces('klass')
        self.assert_(implemented.isOrExtends(IKlass))
        self.assertEqual([iface for iface in implemented], [IKlass])

    def testGetFactoriesFor(self):
        self.assertEqual(list(capi.getFactoriesFor(IKlass)),
                         [('klass', self.factory)])


def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')

