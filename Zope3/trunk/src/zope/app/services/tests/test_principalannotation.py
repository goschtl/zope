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
$Id: test_principalannotation.py,v 1.2 2002/12/25 14:13:20 jim Exp $
"""
from unittest import TestCase, TestLoader, TextTestRunner
from zope.app.services.tests.placefulsetup \
    import PlacefulSetup
from zope.component import getServiceManager, getService
from zope.app.services.principalannotation import PrincipalAnnotationService, Annotations, AnnotationsForPrincipal
from zope.app.interfaces.services.principalannotation import IPrincipalAnnotationService
from zope.component.adapter import provideAdapter
from zope.component import getAdapter
from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.security import IPrincipal


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
