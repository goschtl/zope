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
