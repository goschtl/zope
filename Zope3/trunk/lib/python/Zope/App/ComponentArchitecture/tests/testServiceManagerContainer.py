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
$Id: testServiceManagerContainer.py,v 1.1 2002/08/01 18:42:09 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.ComponentArchitecture.IServiceService import IServiceService
from Zope.App.ComponentArchitecture.IServiceManagerContainer \
     import IServiceManagerContainer
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError
from Interface.Verify import verifyObject
from Zope.ContextWrapper import getbaseobject

class ServiceManager:

    __implements__ =  IServiceService

    ############################################################
    # Implementation methods for interface
    # Zope.ComponentArchitecture.IServiceService.

    def getService(self, object, name):
        '''See interface IServiceService'''
        raise ComponentLookupError(name)

    def getServiceDefinitions(self):
        '''See interface IServiceService'''
        return ()

    #
    ############################################################

class BaseTestServiceManagerContainer:

    """This test is for objects that don't have service managers by
    default and that always give back the service manager they were
    given.


    Subclasses need to define a method, '_Test__new', that takes no
    arguments and that returns a new service manager
    container that has no service manager."""

    def testIServiceManagerContainerVerify(self):
        verifyObject(IServiceManagerContainer, self._Test__new())
    
    def testHas(self):
        smc=self._Test__new()
        self.failIf(smc.hasServiceManager())
        smc.setServiceManager(ServiceManager())
        self.failUnless(smc.hasServiceManager())

    def testGet(self):
        smc=self._Test__new()
        # since the managers are now wrapped, need to look at base object
        self.failUnless(getbaseobject(smc.queryServiceManager()) is None)
        self.assertRaises(ComponentLookupError, smc.getServiceManager)
        sm=ServiceManager()
        smc.setServiceManager(sm)
        self.failUnless(getbaseobject(smc.getServiceManager()) is sm)
        self.failUnless(getbaseobject(smc.queryServiceManager(self)) is sm)

    def testSet(self):
        smc=self._Test__new()
        self.assertRaises(Exception, smc.setServiceManager, self)



class Test(BaseTestServiceManagerContainer, TestCase):
    def _Test__new(self):
        from Zope.App.ComponentArchitecture.ServiceManagerContainer \
             import ServiceManagerContainer
        return ServiceManagerContainer()


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
