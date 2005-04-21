##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Test browser security

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import ZopeTestCase, installProduct
installProduct('Five')

from zope.app import zapi
from Products.Five import zcml
from Products.Five.traversable import FakeRequest
from Products.Five.tests.dummy import Dummy1

class PageSecurityTest(ZopeTestCase):

    def test_page_security(self):
        decl = """
        <configure xmlns="http://namespaces.zope.org/zope"
            xmlns:browser="http://namespaces.zope.org/browser">

          <browser:page
             for="Products.Five.tests.dummy.IDummy"
             class="Products.Five.tests.dummy.DummyView"
             attribute="foo"
             name="test_page_security"
             permission="zope2.ViewManagementScreens"
           />

        </configure>
        """
        zcml.load_string(decl)
        request = FakeRequest()
        # Wrap into an acquisition so that imPermissionRole objects
        # can be evaluated.
        view = zapi.getView(Dummy1(), 'test_page_security', request)

        ac = getattr(view, '__ac_permissions__')
        # It's protecting the object with the permission, and not the
        # attribute, so we get ('',) instead of ('foo',).
        ex_ac = (('View management screens', ('',)),)
        self.assertEquals(ac, ex_ac)

        # Wrap into an acquisition so that imPermissionRole objects
        # can be evaluated. __roles__ is a imPermissionRole object.
        view = view.__of__(self.folder)
        view_roles = getattr(view, '__roles__', None)
        self.failIf(view_roles is None)
        self.failIf(view_roles == ())
        self.assertEquals(view_roles, ('Manager',))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PageSecurityTest))
    return suite

if __name__ == '__main__':
    framework()
