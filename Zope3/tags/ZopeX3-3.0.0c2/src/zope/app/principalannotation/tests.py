##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Principal Annotation Tests

$Id$
"""
from unittest import TestCase, TestLoader, TextTestRunner
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.principalannotation import \
     PrincipalAnnotationService, AnnotationsForPrincipal
from interfaces import IPrincipalAnnotationService
from zope.app.tests import ztapi
from zope.app.annotation.interfaces import IAnnotations
from zope.app.security.interfaces import IPrincipal
from zope.app.tests import setup
from zope.interface import implements
from zope.app import zapi

class Principal(object):

    implements(IPrincipal)

    def __init__(self, id):
        self.id = id


class PrincipalAnnotationTests(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        sm = self.buildFolders(site='/')

        root_sm = zapi.getGlobalServices()

        svc = PrincipalAnnotationService()

        root_sm.defineService("PrincipalAnnotation",
                              IPrincipalAnnotationService)
        root_sm.provideService("PrincipalAnnotation", svc)

        self.svc = setup.addService(sm, 'PrincipalAnnotation', svc)

    def testGetSimple(self):
        prince = Principal('somebody')
        self.assert_(not self.svc.hasAnnotations(prince))

        princeAnnotation = self.svc.getAnnotations(prince)
        # Just getting doesn't actualy store. We don't want to store unless
        # we make a change.
        self.assert_(not self.svc.hasAnnotations(prince))

        princeAnnotation['something'] = 'whatever'

        # But now we should have the annotation:
        self.assert_(self.svc.hasAnnotations(prince))

    def testGetFromLayered(self):
        princeSomebody = Principal('somebody')
        sm1 = self.makeSite('folder1')
        subService = setup.addService(sm1, 'PrincipalAnnotation',
                                      PrincipalAnnotationService())

        parentAnnotation = self.svc.getAnnotations(princeSomebody)

        # Just getting doesn't actualy store. We don't want to store unless
        # we make a change.
        self.assert_(not subService.hasAnnotations(princeSomebody))

        parentAnnotation['hair_color'] = 'blue'

        # But now we should have the annotation:
        self.assert_(self.svc.hasAnnotations(princeSomebody))

        subAnnotation = subService.getAnnotations(princeSomebody)
        self.assertEquals(subAnnotation['hair_color'], 'blue')

        subAnnotation['foo'] = 'bar'

        self.assertEquals(parentAnnotation.get("foo"), None)


    def testAdapter(self):
        p = Principal('somebody')
        ztapi.provideAdapter(IPrincipal, IAnnotations,
                             AnnotationsForPrincipal(self.svc))
        annotations = IAnnotations(p)
        annotations["test"] = "bar"
        annotations = IAnnotations(p)
        self.assertEquals(annotations["test"], "bar")


def test_suite():
    loader=TestLoader()
    return loader.loadTestsFromTestCase(PrincipalAnnotationTests)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
