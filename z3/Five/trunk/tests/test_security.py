import os, sys
from os import curdir
from os.path import join, abspath, dirname, split

try:
    __file__
except NameError:
    # Test was called directly, so no __file__ global exists.
    _prefix = abspath(curdir)
else:
    # Test was called by another test.
    _prefix = abspath(dirname(__file__))

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# XXX hack but no other way to initialize options apparently
from Zope.Startup.run import configure
configure(join(_prefix, '..', '..', '..', 'etc', 'zope.conf'))

import unittest
from Testing import ZopeTestCase

ZopeTestCase.installProduct('Five')

from zope.configuration import xmlconfig
from Products.Five import zcml
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class Dummy1:
    def foo(self): pass
    def bar(self): pass
    def baz(self): pass
    def keg(self): pass
    def wot(self): pass

class Dummy2(Dummy1):
    security = ClassSecurityInfo()
    security.declarePublic('foo')
    security.declareProtected('View management screens', 'bar')
    security.declarePrivate('baz')
    security.declareProtected('View management screens', 'keg')

class SecurityTestCase(ZopeTestCase.ZopeTestCase):

    def test_require(self):
        # Need to use xmlconfig() to run a
        # small zcml snippet and then check
        # the class __ac_permissions__ to see
        # if the declaration took effect.
        pass

    def test_allow(self):
        pass

    def test_initialize(self):
        pass

class SecurityEquivalenceTestCase(ZopeTestCase.ZopeTestCase):

    def setUp(self):
        self.dummy1 = Dummy1
        self.dummy2 = Dummy2
        zcml.initialize()

    def tearDown(self):
        zcml.reset()

    def test_equivalence(self):
        self.failIf(hasattr(self.dummy1, '__ac_permissions__'))
        self.failIf(hasattr(self.dummy2, '__ac_permissions__'))

        decl = """
        <configure xmlns="http://namespaces.zope.org/zope"
            xmlns:five="http://namespaces.zope.org/five">

        <five:content
            class="Five.tests.test_security.Dummy1">

          <allow attributes="foo" />

          <deny attributes="baz" />

          <require attributes="bar keg"
	      permission="zope.ViewManagementScreens"
	      />

        </five:content>
        </configure>
        """
        zcml.string(decl)
        InitializeClass(self.dummy2)
        ac1 = getattr(self.dummy1, '__ac_permissions__')
        ac2 = getattr(self.dummy2, '__ac_permissions__')
        self.assertEquals(ac1, ac2)
        foo_roles1 = getattr(self.dummy1, 'foo__roles__')
        baz_roles1 = getattr(self.dummy1, 'baz__roles__')
        self.assertEquals(foo_roles1, None)
        self.assertEquals(baz_roles1, ())

        foo_roles2 = getattr(self.dummy2, 'foo__roles__')
        baz_roles2 = getattr(self.dummy2, 'baz__roles__')
        self.assertEquals(foo_roles2, None)
        self.assertEquals(baz_roles2, ())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SecurityEquivalenceTestCase))
    suite.addTest(unittest.makeSuite(SecurityTestCase))
    return suite

if __name__ == '__main__':
    framework()

