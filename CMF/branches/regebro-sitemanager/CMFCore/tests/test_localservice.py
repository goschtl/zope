import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
#ZopeTestCase.installProduct('Five')
from zope.app.tests.placelesssetup import setUp, tearDown

from zope.interface import implements, Interface
from OFS.SimpleItem import SimpleItem

import Products.Five
from Products.Five import zcml

def Wrapper(ob, container):
    return ob.__of__(container)

class IDummyUtility(Interface):
    pass

class DummyUtility(SimpleItem):
    implements(IDummyUtility)

from Products.CMFCore.PortalObject import PortalObjectBase
from Products.Five.localsite import SimpleLocalUtilityService
from zope.app.component.localservice import getLocalServices
from zope.component.exceptions import ComponentLookupError
from zope.component import getService, getServices
from Products.Five.localsite import LocalService, SimpleLocalUtilityService
from zope.component.servicenames import Utilities

class PortalUtility(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        setUp()
        zcml.load_config("meta.zcml", Products.Five)
        zcml.load_config("localsite.zcml", Products.Five)
        zcml_text = """<configure 
          xmlns="http://namespaces.zope.org/zope"
          xmlns:five="http://namespaces.zope.org/five">
          <five:localsite class="Products.CMFCore.PortalObject.PortalObjectBase" />
        </configure>"""
        zcml.load_string(zcml_text)
        
        portal = PortalObjectBase('portal')
        self.app._setObject('portal', portal)
        
    def beforeTearDown(self):
        self.app._delObject('portal')
        tearDown()

    def test_getServices(self):
        serviceservice = getServices(self.app.portal)
        self.failUnless(isinstance(serviceservice, LocalService))
        service = getService(Utilities, self.app.portal)
        self.failUnless(isinstance(service, SimpleLocalUtilityService))
            
    def test_getUtility(self):
        service = getService(Utilities, self.app.portal)
        dummy1 = DummyUtility()
        service.registerUtility(IDummyUtility, dummy1, 'dummy1')
        dummy2 = DummyUtility()
        service.registerUtility(IDummyUtility, dummy2, 'dummy2')
        service = getService(Utilities, self.app.portal)
        # Interface only:
        
        # By name
        utility = service.getUtility(IDummyUtility, 'dummy1')
        self.failUnless(utility.aq_base is dummy1)
        utility = service.getUtility(IDummyUtility, 'dummy2')
        self.failUnless(utility.aq_base is dummy2)
        
        # Get both
        import pdb;pdb.set_trace()
        utilities = service.getUtilitiesFor(IDummyUtility)
        i = 0
        for x in utilities.next():
            i += 1
        self.failUnlessEqual(i, 2)
        
    def test_getUnnamedUtilities(self):
        service = getService(Utilities, self.app.portal)
        dummy1 = DummyUtility()
        service.registerUtility(IDummyUtility, dummy1, 'dummy1')
        dummy2 = DummyUtility()
        service.registerUtility(IDummyUtility, dummy2)
        service = getService(Utilities, self.app.portal)
        utility = service.getUtility(IDummyUtility)
        self.failUnless(utility.aq_base is dummy2)
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PortalUtility))
    return suite

if __name__ == '__main__':
    framework()
