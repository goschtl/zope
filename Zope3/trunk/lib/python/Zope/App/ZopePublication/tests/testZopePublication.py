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
import unittest

from Interface.Verify import verifyClass
from Interface.Implements import instancesOfObjectImplements

from ZODB.MappingStorage import DB

from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture.GlobalAdapterService import provideAdapter 

from Zope.I18n.IUserPreferredCharsets import IUserPreferredCharsets

from Zope.Publisher.DefaultPublication import TestPublication
from Zope.Publisher.HTTP.HTTPRequest import IHTTPRequest
from Zope.Publisher.HTTP.HTTPCharsets import HTTPCharsets

from Zope.Security import SimpleSecurityPolicies
from Zope.Security.SecurityManagement import setSecurityPolicy

from Zope.App.Security.Registries.PrincipalRegistry import principalRegistry
from Zope.App.Security.IUnauthenticatedPrincipal \
     import IUnauthenticatedPrincipal

from Zope.App.ZopePublication.ZopePublication import ZopePublication

from Zope.App.OFS.Content.Folder.Folder import Folder
from Zope.App.OFS.Content.Folder.RootFolder import RootFolder

from Zope.ComponentArchitecture.IServiceService import IServiceService

from Zope.Publisher.BaseRequest import TestRequest

from Zope.ComponentArchitecture.GlobalServiceManager import serviceManager

from Transaction import get_transaction

class BasePublicationTests(PlacelessSetup, unittest.TestCase):
    klass = ZopePublication 
    
    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(IHTTPRequest, IUserPreferredCharsets, HTTPCharsets)    
        self.policy = setSecurityPolicy(
            SimpleSecurityPolicies.PermissiveSecurityPolicy()
            )
        self.db = DB("foo")

        connection = self.db.open()
        root = connection.root()
        app = getattr(root, ZopePublication.root_name, None)

        if app is None:
            from Zope.App.OFS.Content.Folder.RootFolder import RootFolder

            app = RootFolder()
            root[ZopePublication.root_name] = app

            get_transaction().commit()

        connection.close()
        
        from Zope.App.Traversing.Namespaces import provideNamespaceHandler
        from Zope.App.Traversing.PresentationNamespaces import view, resource
        from Zope.App.Traversing.EtcNamespace import etc
        provideNamespaceHandler('view', view)
        provideNamespaceHandler('resource', resource)
        provideNamespaceHandler('etc', etc)

    def tearDown(self):
        setSecurityPolicy(self.policy) # XXX still needed?
        PlacelessSetup.tearDown(self)

    def testInterfacesVerify(self):
        for interface in instancesOfObjectImplements(self.klass):
            verifyClass(interface, TestPublication)

class Principal:
    def __init__(self, id): self._id = id
    def getId(self): return self._id
    def getTitle(self): return ''
    def getDescription(self): return ''

class UnauthenticatedPrincipal(Principal):
    __implements__ = IUnauthenticatedPrincipal


class AuthService1:

    def authenticate(self, request):
        return None

    def unauthenticatedPrincipal(self):
        return 'test.anonymous'

    def unauthorized(self, id, request):
        pass

    def getPrincipal(self, id):
        return UnauthenticatedPrincipal(id)
        

class AuthService2(AuthService1):

    def authenticate(self, request):
        return 'test.bob'

    def getPrincipal(self, id):
        return Principal(id)
        

class ServiceManager:

    __implements__ = IServiceService # a dirty lie
    
    def __init__(self, auth):   self.auth = auth
    def get(self, key, d=None):      return self.auth
    __getitem__ = get
    def __contains__(self, key): return 1

    def getService(self, name):
        # I just wanna get the test to pass. Waaaaa
        return serviceManager.getService(name)


class ZopePublicationTests(BasePublicationTests):
    klass = ZopePublication

    def testPlacefulAuth(self):
        principalRegistry.defineDefaultPrincipal('anonymous', '')
        
        root = self.db.open().root()
        app = root[ZopePublication.root_name]
        app.setObject('f1', Folder())
        f1 = app['f1']
        f1.setObject('f2', Folder())
        f1.setServiceManager(ServiceManager(AuthService1()))
        f2 = f1['f2']
        f2.setServiceManager(ServiceManager(AuthService2()))
        get_transaction().commit()

        request = TestRequest('/f1/f2')

        from Zope.ComponentArchitecture.GlobalViewService import provideView
        from Zope.App.OFS.Container.IContainer import ISimpleReadContainer
        from Zope.App.OFS.Container.ContainerTraverser \
             import ContainerTraverser
        from Zope.ComponentArchitecture.IPresentation import IPresentation
        provideView(ISimpleReadContainer, '_traverse', IPresentation,
                    ContainerTraverser)

        from Zope.App.OFS.Content.Folder.Folder import IFolder
        from Zope.Security.Checker import defineChecker, InterfaceChecker
        defineChecker(Folder, InterfaceChecker(IFolder))
        defineChecker(RootFolder, InterfaceChecker(IFolder))

        request.setViewType(IPresentation)

        publication = self.klass(self.db)

        publication.beforeTraversal(request)
        self.assertEqual(request.user.getId(), 'anonymous')
        root = publication.getApplication(request)
        publication.callTraversalHooks(request, root)
        self.assertEqual(request.user.getId(), 'anonymous')
        ob = publication.traverseName(request, root, 'f1')
        publication.callTraversalHooks(request, ob)
        self.assertEqual(request.user.getId(), 'test.anonymous')
        ob = publication.traverseName(request, ob, 'f2')
        publication.afterTraversal(request, ob)
        self.assertEqual(request.user.getId(), 'test.bob')
        
def test_suite():
    return unittest.makeSuite(ZopePublicationTests, 'test')

if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )
