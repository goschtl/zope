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
$Id: testPrincipalAnnotation.py,v 1.1 2002/12/04 10:41:33 itamar Exp $
"""
from unittest import TestCase, TestLoader, TextTestRunner
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
    import PlacefulSetup
from Zope.ComponentArchitecture import getServiceManager, getService
from Zope.App.OFS.Services.PrincipalAnnotationService.PrincipalAnnotationService import PrincipalAnnotationService, Annotations, AnnotationsForPrincipal
from Zope.App.OFS.Services.PrincipalAnnotationService.IPrincipalAnnotationService import IPrincipalAnnotationService
from Zope.ComponentArchitecture.GlobalAdapterService import provideAdapter
from Zope.ComponentArchitecture import getAdapter
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.Security.IPrincipal import IPrincipal


class Principal:

    __implements__ = IPrincipal
    
    def __init__(self, id):
        self.id = id

    def getId(self):
        return self.id


class PrincipalAnnotationTests(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()

        root_sm = getServiceManager(None)

        svc = PrincipalAnnotationService()

        root_sm.defineService("PrincipalAnnotation", IPrincipalAnnotationService)
        root_sm.provideService("PrincipalAnnotation", svc)

        self.createServiceManager()
        
        sm = getServiceManager(self.rootFolder)
        sm.PrincipalAnnotation = svc
        
        self.svc = getService(self.rootFolder, "PrincipalAnnotation")

    def testGetSimple(self):
        prince = Principal('somebody')
        self.assert_(not self.svc.hasAnnotation(prince.getId()))

        princeAnnotation = self.svc.getAnnotation(prince.getId())
        self.assert_(self.svc.hasAnnotation(prince.getId()))

        princeAnnotation['something'] = 'whatever'

    def testGetFromLayered(self):
        princeSomebody = Principal('somebody')
        self.createServiceManager(self.folder1)
        sm1 = getServiceManager(self.folder1)
        sm1.PrincipalAnnotation = PrincipalAnnotationService()
        subService = getService(self.folder1, "PrincipalAnnotation")

        parentAnnotation = self.svc.getAnnotation(princeSomebody.getId())
        self.assert_(self.svc.hasAnnotation(princeSomebody.getId()))
        self.assert_(not subService.hasAnnotation(princeSomebody.getId()))
        
        parentAnnotation['hair_color'] = 'blue'

        subAnnotation = subService.getAnnotation(princeSomebody.getId())
        self.assertEquals(subAnnotation['hair_color'], 'blue')

        subAnnotation['foo'] = 'bar'

        self.assertEquals(parentAnnotation.get("foo"), None)


    def testAdapter(self):
        p = Principal('somebody')
        provideAdapter(IPrincipal, IAnnotations, AnnotationsForPrincipal(self.svc))
        annotations = getAdapter(p, IAnnotations)
        annotations["test"] = "bar"
        annotations = getAdapter(p, IAnnotations)
        self.assertEquals(annotations["test"], "bar")

        
def test_suite():
    loader=TestLoader()
    return loader.loadTestsFromTestCase(PrincipalAnnotationTests)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
