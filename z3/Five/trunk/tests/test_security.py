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
from zope.component import getView
from zope.interface import Interface, implements
from zope.testing.cleanup import CleanUp
from Products.Five import zcml
from Products.Five.browser import BrowserView
from Products.Five.viewable import FakeRequest
from Products.Five.security.permission import clearSecurityInfo
from AccessControl import ClassSecurityInfo
from AccessControl.PermissionRole import PermissionRole
from Globals import InitializeClass

class IDummy(Interface):
    """Just a marker interface"""

class DummyView(BrowserView):
    """A dummy view"""

    def foo(self):
        """A foo"""
        return 'A foo view'

class Dummy1:
    implements(IDummy)
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

class PageSecurityTestCase(CleanUp, ZopeTestCase.ZopeTestCase):

    def setUp(self):
        super(PageSecurityTestCase, self).setUp()
        zcml.reset()
        zcml.initialize()
        self.dummy1 = Dummy1

    def tearDown(self):
        super(PageSecurityTestCase, self).tearDown()
        zcml.reset()
        clearSecurityInfo(self.dummy1)

    def test_page_security(self):
        self.failIf(hasattr(self.dummy1, '__ac_permissions__'))

        decl = """
        <configure xmlns="http://namespaces.zope.org/zope"
            xmlns:five="http://namespaces.zope.org/five">

          <five:page
             for="Five.tests.test_security.IDummy"
             class="Five.tests.test_security.DummyView"
             attribute="foo"
             name="foo.txt"
             permission="zope.ViewManagementScreens"
           />

        </configure>
        """
        zcml.string(decl)
        request = FakeRequest()
        view = getView(Dummy1(), 'foo.txt', request)

        ac = getattr(view, '__ac_permissions__')
        ex_ac = (('View management screens', ('foo',)),)
        self.assertEquals(ac, ex_ac)
        foo_roles = getattr(view, 'foo__roles__', None)
        self.failIf(foo_roles is None)
        self.failIf(foo_roles == ())
        self.assertEquals(foo_roles.__of__(view), ('Manager',))

class SecurityEquivalenceTestCase(CleanUp, ZopeTestCase.ZopeTestCase):

    def setUp(self):
        super(SecurityEquivalenceTestCase, self).setUp()
        zcml.reset()
        zcml.initialize()
        self.dummy1 = Dummy1
        self.dummy2 = Dummy2

    def tearDown(self):
        zcml.reset()
        super(SecurityEquivalenceTestCase, self).tearDown()
        clearSecurityInfo(self.dummy1)
        clearSecurityInfo(self.dummy2)

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

        bar_roles1 = getattr(self.dummy1, 'bar__roles__').__of__(self.dummy1)
        self.assertEquals(bar_roles1.__of__(self.dummy1), ('Manager',))

        keg_roles1 = getattr(self.dummy1, 'keg__roles__').__of__(self.dummy1)
        self.assertEquals(keg_roles1.__of__(self.dummy1), ('Manager',))

        foo_roles1 = getattr(self.dummy1, 'foo__roles__')
        self.assertEquals(foo_roles1, None)

        baz_roles1 = getattr(self.dummy1, 'baz__roles__')
        self.assertEquals(baz_roles1, ())

        bar_roles2 = getattr(self.dummy2, 'bar__roles__').__of__(self.dummy2)
        self.assertEquals(bar_roles2.__of__(self.dummy2), ('Manager',))

        keg_roles2 = getattr(self.dummy2, 'keg__roles__').__of__(self.dummy2)
        self.assertEquals(keg_roles2.__of__(self.dummy2), ('Manager',))

        foo_roles2 = getattr(self.dummy2, 'foo__roles__')
        self.assertEquals(foo_roles2, None)

        baz_roles2 = getattr(self.dummy2, 'baz__roles__')
        self.assertEquals(baz_roles2, ())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SecurityEquivalenceTestCase))
    suite.addTest(unittest.makeSuite(PageSecurityTestCase))
    return suite

if __name__ == '__main__':
    framework()
