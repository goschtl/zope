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

Revision information:
$Id: testAdder.py,v 1.2 2002/06/10 23:28:13 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.OFS.Container.Views.Browser.tests.AdderBaseTests \
     import BaseRegistryTest, BaseAddingTest
from Zope.App.OFS.Services.AddableService.tests.AddableSetup import \
  AddableSetup
from Zope.ComponentArchitecture import getServiceManager

class Methods(AddableSetup):
    # Supply the methods needed by the bases.

    def _TestView__newContext(self):
        from Zope.App.OFS.Services.ServiceManager.ServiceManager \
             import ServiceManager
        return ServiceManager()

    def _TestView__newView(self, container):
        from Zope.App.OFS.Services.ServiceManager.Views.Browser.Adder \
             import Adder 
        return Adder(container, None)

    def _TestAdderView__registry(self):
        return 'AddableServices'


class RegistryTest(Methods, BaseRegistryTest, TestCase): pass
class AddingTest(Methods, BaseAddingTest, TestCase):
    def setUp(self):
        Methods.setUp(self)
        BaseAddingTest.setUp(self)

def test_suite():
    return TestSuite([makeSuite(RegistryTest),
                      makeSuite(AddingTest),
                      ])

if __name__=='__main__':
    main(defaultTest='test_suite')
