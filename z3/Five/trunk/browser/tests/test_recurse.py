##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Test default view recursion

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import installProduct
installProduct('Five')

from OFS.Traversable import Traversable
from zope.interface import Interface, implements
from Products.Five.fiveconfigure import classDefaultViewable

class IRecurse(Interface):
    pass

class Recurse(Traversable):
    implements(IRecurse)

    def view(self):
        return self()

    def __call__(self):
        return 'foo'

classDefaultViewable(Recurse)

class RecursionTest(unittest.TestCase):

    def setUp(self):
        self.ob = Recurse()

    def test_recursive_call(self):
        from zope.app import zapi
        from zope.publisher.interfaces.browser import IBrowserRequest
        pres = zapi.getGlobalService('Presentation')
        pres.setDefaultViewName(IRecurse, IBrowserRequest, 'view')
        self.assertEquals(self.ob.view(), 'foo')
        self.assertEquals(self.ob(), 'foo')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RecursionTest))
    return suite

if __name__ == '__main__':
    framework()
