import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
ZopeTestCase.installProduct('Five')

from zope.interface import implements
from zope.interface import directlyProvides, directlyProvidedBy
from zope.interface import Interface
from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IServiceService
from zope.component.service import serviceManager
from zope.component.servicenames import Utilities
from zope.component import getGlobalServices, getServices, getService
from zope.app.component.hooks import getServices_hook
from zope.app.component.hooks import setSite, getSite
from zope.app.site.interfaces import IPossibleSite, ISite, ISiteManager
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.tests.placelesssetup import setUp, tearDown

from Acquisition import Implicit
from OFS.ObjectManager import ObjectManager
from OFS.SimpleItem import SimpleItem

import Products.Five
from Products.Five import zcml

class ServiceManager(Implicit):
    implements(ISiteManager)

    def __init__(self):
        self.dummy_service = object()

    def getService(self, name):
        if name == 'dummy':
            return self.dummy_service
        raise ComponentLookupError(name)

class Folder(ObjectManager):
    implements(IPossibleSite)

    sm = None

    def getId(self):
        return self.id

    def getSiteManager(self, default=None):
        return self.sm

    def setSiteManager(self, sm):
        self.sm = sm
        directlyProvides(self, ISite, directlyProvidedBy(self))

class Package(Implicit):
    pass

class Root(Folder):
    implements(IContainmentRoot, ISite)
    def getSiteManager(self):
        return getGlobalServices()

class ServiceServiceStub(object):
    implements(IServiceService)

def Wrapper(ob, container):
    return ob.__of__(container)

class IDummyUtility(Interface):
    pass

class DummyUtility(SimpleItem):
    implements(IDummyUtility)

class Test(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        setUp()
        root = Wrapper(self.folder, Root())

        f1 = Wrapper(Folder(), root)
        sm1 = ServiceManager()
        f1.setSiteManager(sm1)
        p1 = Wrapper(Package(), sm1)

        f2 = Wrapper(Folder(), f1)
        sm2 = ServiceManager()
        f2.setSiteManager(sm2)
        p2 = Wrapper(Package(), sm2)

        sm1.next = serviceManager
        sm2.next = sm1

        self.root = root
        self.f1 = f1
        self.f2 = f2
        self.sm1 = sm1
        self.sm2 = sm2
        self.p1 = p1
        self.p2 = p2
        self.unparented_folder = Folder()
        self.unrooted_subfolder = Wrapper(Folder(), self.unparented_folder)
        zcml.load_config("meta.zcml", Products.Five)
        zcml.load_config("localsite.zcml", Products.Five)
        zcml_text = """<configure 
          xmlns="http://namespaces.zope.org/zope"
          xmlns:five="http://namespaces.zope.org/five">
          <five:localsite class="Products.Five.testing.localsite.DummySite" />
        </configure>"""
        zcml.load_string(zcml_text)

    def beforeTearDown(self):
        setSite()
        tearDown()

    def test_getServices(self):
        self.assertEqual(getServices_hook(None), serviceManager)
        self.assertEqual(getServices_hook(self.root), serviceManager)
        self.assertEqual(getServices_hook(self.f1), self.sm1)
        self.assertEqual(getServices_hook(self.f2), self.sm2)
        setSite(self.f2)
        self.assertEqual(getServices_hook(None), self.sm2)

    def test_queryNextService(self):
        from zope.app.component.localservice import queryNextService
        self.assert_(queryNextService(self.sm2, 'dummy') is
                     self.sm1.dummy_service)
        self.assert_(queryNextService(self.p2, 'dummy') is
                     self.sm1.dummy_service)
        marker = object()
        self.assert_(queryNextService(self.p1, 'dummy', marker) is marker)

    def test_getNextService(self):
        from zope.app.component.localservice import getNextService
        self.assert_(getNextService(self.sm2, 'dummy') is
                     self.sm1.dummy_service)
        self.assert_(getNextService(self.p2, 'dummy') is
                     self.sm1.dummy_service)
        self.assertRaises(ComponentLookupError,
                          getNextService, self.p1, 'dummy')


    def test_queryNextServices(self):
        from zope.app.component.localservice import queryNextServices
        marker = object()
        self.assert_(queryNextServices(self.root, marker) is marker)
        self.assert_(queryNextServices(self.f1, marker) is marker)
        self.assert_(queryNextServices(self.f2, marker) is marker)
        self.assertEqual(queryNextServices(self.sm1), serviceManager)
        self.assertEqual(queryNextServices(self.sm2), self.sm1)
        self.assertEqual(queryNextServices(self.p1), serviceManager)
        self.assertEqual(queryNextServices(self.p2), self.sm1)

        self.assert_(queryNextServices(self.unparented_folder, marker)
                     is marker)
        self.assert_(queryNextServices(self.unrooted_subfolder, marker)
                     is marker)

    def test_getNextServices(self):
        from zope.app.component.localservice import getNextServices
        self.assertRaises(ComponentLookupError,
                          getNextServices, self.root)
        self.assertRaises(ComponentLookupError,
                          getNextServices, self.f1)
        self.assertRaises(ComponentLookupError,
                          getNextServices, self.f2)
        self.assertEqual(getNextServices(self.sm1), serviceManager)
        self.assertEqual(getNextServices(self.sm2), self.sm1)
        self.assertEqual(getNextServices(self.p1), serviceManager)
        self.assertEqual(getNextServices(self.p2), self.sm1)

        self.assertRaises(ComponentLookupError,
                          getNextServices, self.unparented_folder)
        self.assertRaises(ComponentLookupError,
                          getNextServices, self.unrooted_subfolder)

# XXX Maybe we need to test this with RestrictedPython in the context
# of Zope2? Maybe we just don't care.
#
#     def test_getNextServices_security(self):
#         from zope.app.component.localservice import getNextServices
#         from zope.security.checker import ProxyFactory, NamesChecker
#         sm = ProxyFactory(self.sm1, NamesChecker(('next',)))
#         # Check that serviceManager is not proxied
#         self.assert_(getNextServices(sm) is serviceManager)

    def test_queryLocalServices(self):
        from zope.app.component.localservice import queryLocalServices
        marker = object()
        self.assert_(queryLocalServices(self.root, marker) is marker)
        self.assert_(queryLocalServices(self.f1, marker) is marker)
        self.assert_(queryLocalServices(self.f2, marker) is marker)
        self.assertEqual(queryLocalServices(self.sm1), self.sm1)
        self.assertEqual(queryLocalServices(self.sm2), self.sm2)
        self.assertEqual(queryLocalServices(self.p1), self.sm1)
        self.assertEqual(queryLocalServices(self.p2), self.sm2)

        self.assert_(queryLocalServices(self.unparented_folder, marker)
                     is marker)
        self.assert_(queryLocalServices(self.unrooted_subfolder, marker)
                     is marker)

    def test_getLocalServices(self):
        from zope.app.component.localservice import getLocalServices
        self.assertRaises(ComponentLookupError,
                          getLocalServices, self.root)
        self.assertRaises(ComponentLookupError,
                          getLocalServices, self.f1)
        self.assertRaises(ComponentLookupError,
                          getLocalServices, self.f2)
        self.assertEqual(getLocalServices(self.sm1), self.sm1)
        self.assertEqual(getLocalServices(self.sm2), self.sm2)
        self.assertEqual(getLocalServices(self.p1), self.sm1)
        self.assertEqual(getLocalServices(self.p2), self.sm2)

        unparented_folder = Folder()
        self.assertRaises(ComponentLookupError,
                          getLocalServices, unparented_folder)
        unrooted_subfolder = Wrapper(Folder(), unparented_folder)
        self.assertRaises(ComponentLookupError,
                          getLocalServices, unrooted_subfolder)

    def test_serviceServiceAdapter(self):
        from Products.Five.localsite import serviceServiceAdapter

        # If it is a site, return the service service.
        ss = ServiceServiceStub()
        site = Folder()
        site.setSiteManager(ss)
        self.assertEqual(serviceServiceAdapter(site), ss)

        # If it has an acquisition context, "acquire" the site
        # and return the service service
        ob = Folder()
        ob = ob.__of__(site)
        self.assertEqual(serviceServiceAdapter(ob), ss)
        ob2 = Folder()
        ob2 = ob2.__of__(ob)
        self.assertEqual(serviceServiceAdapter(ob2), ss)

        # If it does we are unable to find a service service, raise
        # ComponentLookupError
        orphan = Folder()
        self.assertRaises(ComponentLookupError, serviceServiceAdapter, orphan)

    def test_setThreadSite_clearThreadSite(self):
        from zope.app.component.localservice import threadSiteSubscriber
        from zope.app.component.localservice import clearSite
        from zope.app.publication.zopepublication import BeforeTraverseEvent

        self.assertEqual(getSite(), None)

        # A non-site is traversed
        ob = object()
        request = object()
        ev = BeforeTraverseEvent(ob, request)
        threadSiteSubscriber(ev)

        self.assertEqual(getSite(), None)

        # A site is traversed
        ss = ServiceServiceStub()
        site = Folder()
        site.setSiteManager(ss)

        ev = BeforeTraverseEvent(site, request)
        threadSiteSubscriber(ev)

        self.assertEqual(getSite(), site)

        clearSite()

        self.assertEqual(getSite(), None)

class BeforeTraversalTest(ZopeTestCase.FunctionalTestCase):

    def afterSetUp(self):
        setUp()
        zcml.load_config("meta.zcml", Products.Five)
        zcml.load_config("localsite.zcml", Products.Five)
        zcml_text = """<configure xmlns:five="http://namespaces.zope.org/five">
        <five:localsite class="Products.Five.testing.localsite.DummySite" />
        </configure>"""
        zcml.load_string(zcml_text)

    def beforeTearDown(self):
        from zope.app.component.localservice import clearSite
        clearSite()
        tearDown()

    def test_before_traversal_event_and_hook(self):
        return
        from Products.Five.localsite import enableLocalSiteHook
        f1 = Folder()
        f1.id = 'f1'
        self.folder._setObject('f1', f1)
        f1 = self.folder._getOb('f1')
        ss = ServiceServiceStub()
        f1.setSiteManager(ss)
        enableLocalSiteHook(f1)
        path = '/'.join(f1.getPhysicalPath())
        response = self.publish(path)
        self.assertEqual(getServices(), ss)

    def test_no_before_traversal_event(self):
        path = '/'.join(self.folder.getPhysicalPath())
        response = self.publish(path)
        self.assertEqual(getSite(), None)

class LocalUtilityServiceTest(ZopeTestCase.FunctionalTestCase):

    def afterSetUp(self):
        setUp()
        from Products.Five.localsite import enableLocalSiteHook
        from Products.Five.testing.localsite import manage_addDummySite
        zcml.load_config("meta.zcml", Products.Five)
        zcml.load_config("localsite.zcml", Products.Five)
        zcml_text = """<configure xmlns:five="http://namespaces.zope.org/five">
        <five:localsite class="Products.Five.testing.localsite.DummySite" />
        </configure>"""
        zcml.load_string(zcml_text)
        manage_addDummySite(self.folder, 'site')
        self.site = self.folder.site
        self.site.manage_addFolder('utilities')
        self.utils = self.site.utilities
        enableLocalSiteHook(self.site)
        self.path = '/'.join(self.site.getPhysicalPath())
        # Traverse to the site so that the local-thread site gets
        # setup correctly.
        self.publish(self.path)

    def beforeTearDown(self):
        from zope.app.component.localservice import clearSite
        clearSite()
        tearDown()

    def test_getServicesHook(self):
        from Products.Five.localsite import LocalService
        local_sm = getServices(None)
        self.failIf(local_sm is serviceManager)
        self.failUnless(isinstance(local_sm, LocalService))

        local_sm = getServices(self.site)
        self.failIf(local_sm is serviceManager)
        self.failUnless(isinstance(local_sm, LocalService))

    def test_getUtilityService(self):
        from Products.Five.localsite import SimpleLocalUtilityService
        utils = getService(Utilities)
        self.failUnless(isinstance(utils, SimpleLocalUtilityService))

        self.assertRaises(ComponentLookupError, utils.getUtility, IDummyUtility)

        self.utils._setObject('dummy', DummyUtility('dummy'))
        dummy = self.utils._getOb('dummy')
        self.assertEquals(utils.getUtility(IDummyUtility, name='dummy'), dummy)

        self.assertEquals(list(utils.getUtilitiesFor(IDummyUtility)), 
                          [('',dummy)])
        self.assertEquals(list(utils.getAllUtilitiesRegisteredFor(
            IDummyUtility)), [dummy])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    suite.addTest(unittest.makeSuite(BeforeTraversalTest))
    suite.addTest(unittest.makeSuite(LocalUtilityServiceTest))
    return suite

if __name__ == '__main__':
    framework()
