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
$Id: testNextService.py,v 1.2 2002/07/11 18:21:28 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Interface import Interface

from Zope.ComponentArchitecture.Exceptions import ComponentLookupError

from Zope.ContextWrapper import Wrapper

from Zope.ComponentArchitecture.IServiceManagerContainer \
     import IServiceManagerContainer

from Zope.ComponentArchitecture.IServiceService import IServiceService

class ServiceManager:
    __implements__ =  IServiceService
        
class Folder:
    __implements__ =  IServiceManagerContainer

    sm = None

    def getServiceManager(self, default=None):
        return self.sm

    def hasServiceManager(self):
        return self.sm

    def setServiceManager(self, sm):
        self.sm = sm

root = Folder()

f1 = Wrapper(Folder(), root)
sm1 = ServiceManager()
f1.setServiceManager(sm1)

f2 = Wrapper(Folder(), f1)
sm2 = ServiceManager()
f2.setServiceManager(sm2)

class Test(TestCase):

    def test_getServiceManager(self):
        from Zope.ComponentArchitecture.GlobalServiceManager \
             import serviceManager
        from Zope.App.ComponentArchitecture.hooks import getServiceManager_hook

        self.assertEqual(getServiceManager_hook(root), serviceManager)
        self.assertEqual(getServiceManager_hook(f1), sm1)
        self.assertEqual(getServiceManager_hook(f2), sm2)

    def test_getNextServiceManager(self):
        from Zope.ComponentArchitecture.GlobalServiceManager \
             import serviceManager
        from Zope.App.ComponentArchitecture.hooks \
             import getNextServiceManager_hook

        self.assertRaises(ComponentLookupError,
                          getNextServiceManager_hook, root)

        self.assertEqual(getNextServiceManager_hook(Wrapper(sm1, f1)),
                                                    serviceManager)
        self.assertEqual(getNextServiceManager_hook(Wrapper(sm2, f2)), sm1)
        

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')



