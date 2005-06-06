##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Test security induced by ZCML

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import ZopeTestCase, installProduct
installProduct('Five')

from zope.interface import Interface, implements
from zope.testing.cleanup import CleanUp
from Products.Five import zcml
from Products.Five.security import clearSecurityInfo, checkPermission
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

class IDummy(Interface):
    """Just a marker interface"""

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

# reimport so that __main__.Dummy{1,2} and test_security.Dummy{1,2}
# are the same objects.
from Products.Five.tests.test_security import Dummy1, Dummy2

class SecurityEquivalenceTest(ZopeTestCase):

    def setUp(self):
        self.dummy1 = Dummy1
        self.dummy2 = Dummy2

    def tearDown(self):
        clearSecurityInfo(self.dummy1)
        clearSecurityInfo(self.dummy2)

    def test_equivalence(self):
        self.failIf(hasattr(self.dummy1, '__ac_permissions__'))
        self.failIf(hasattr(self.dummy2, '__ac_permissions__'))

        decl = """
        <configure xmlns="http://namespaces.zope.org/zope">
          <content class="Products.Five.tests.test_security.Dummy1">

            <allow attributes="foo" />

            <!-- XXX not yet supported
            <deny attributes="baz" />
            -->

            <require attributes="bar keg"
                     permission="zope2.ViewManagementScreens"
                     />

          </content>
        </configure>
        """
        zcml.load_string(decl)
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

        # XXX Not yet supported.
        # baz_roles1 = getattr(self.dummy1, 'baz__roles__')
        # self.assertEquals(baz_roles1, ())

        bar_roles2 = getattr(self.dummy2, 'bar__roles__').__of__(self.dummy2)
        self.assertEquals(bar_roles2.__of__(self.dummy2), ('Manager',))

        keg_roles2 = getattr(self.dummy2, 'keg__roles__').__of__(self.dummy2)
        self.assertEquals(keg_roles2.__of__(self.dummy2), ('Manager',))

        foo_roles2 = getattr(self.dummy2, 'foo__roles__')
        self.assertEquals(foo_roles2, None)

        baz_roles2 = getattr(self.dummy2, 'baz__roles__')
        self.assertEquals(baz_roles2, ())

class CheckPermissionTest(ZopeTestCase):

    def test_publicPermissionId(self):
        self.failUnless(checkPermission('zope2.Public', self.folder))

    def test_privatePermissionId(self):
        self.failIf(checkPermission('zope.Private', self.folder))
        self.failIf(checkPermission('zope2.Private', self.folder))

    def test_accessPermissionId(self):
        self.failUnless(checkPermission('zope2.AccessContentsInformation',
                                        self.folder))

    def test_invalidPermissionId(self):
        self.failIf(checkPermission('notapermission', self.folder))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SecurityEquivalenceTest))
    suite.addTest(unittest.makeSuite(CheckPermissionTest))
    return suite

if __name__ == '__main__':
    framework()
