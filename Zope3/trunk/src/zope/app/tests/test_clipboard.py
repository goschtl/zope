from zope.app.services.tests.test_auth import AuthSetup
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
$Id: test_clipboard.py,v 1.2 2003/02/11 16:00:00 sidnei Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.interfaces.copy import IPrincipalClipboard
from zope.app.copy import PrincipalClipboard
from zope.app.interfaces.services.auth import IUser
from zope.component import getAdapter, getService, getServiceManager
from zope.component.adapter import provideAdapter
from zope.app.services.principalannotation \
    import PrincipalAnnotationService
from zope.app.interfaces.services.principalannotation \
    import IPrincipalAnnotationService
from zope.app.services.tests.placefulsetup \
    import PlacefulSetup
from zope.app.interfaces.annotation import IAnnotations
 
class PrincipalClipboardTest(AuthSetup, PlacefulSetup, TestCase):
    
    def setUp(self):
        AuthSetup.setUp(self)
        PlacefulSetup.setUp(self)
        self.buildFolders()

        provideAdapter(IAnnotations, IPrincipalClipboard, PrincipalClipboard)
        root_sm = getServiceManager(None)
        svc = PrincipalAnnotationService()
        root_sm.defineService("PrincipalAnnotation", \
            IPrincipalAnnotationService) 
        root_sm.provideService("PrincipalAnnotation", svc)
        sm = getServiceManager(self.rootFolder)
        sm.PrincipalAnnotation = svc
        self.svc = getService(self.rootFolder, "PrincipalAnnotation")

    def testAddItems(self):
        auth = self._auth
        user = auth.getPrincipalByLogin('srichter')

        annotationsvc = getService(self, 'PrincipalAnnotation')
        annotations = annotationsvc.getAnnotation(user)
        clipboard = getAdapter(annotations, IPrincipalClipboard)
        clipboard.addItems('move', ['bla', 'bla/foo', 'bla/bar'])
        expected = ({'action':'move', 'target':'bla'}, 
                    {'action':'move', 'target':'bla/foo'},
                    {'action':'move', 'target':'bla/bar'})
                    
        self.failUnless(clipboard.getContents() == expected)
        clipboard.addItems('copy', ['bla'])
        expected = expected + ({'action':'copy', 'target':'bla'},) 
        self.failUnless(clipboard.getContents() == expected)

    def testSetContents(self):
        auth = self._auth
        user = auth.getPrincipalByLogin('srichter')

        annotationsvc = getService(self, 'PrincipalAnnotation')
        annotations = annotationsvc.getAnnotation(user)
        clipboard = getAdapter(annotations, IPrincipalClipboard)

        expected = ({'action':'move', 'target':'bla'}, 
                    {'action':'move', 'target':'bla/foo'},
                    {'action':'move', 'target':'bla/bar'})
        clipboard.setContents(expected)
        self.failUnless(clipboard.getContents() == expected)
        clipboard.addItems('copy', ['bla'])
        expected = expected + ({'action':'copy', 'target':'bla'},) 
        self.failUnless(clipboard.getContents() == expected)

    def testClearContents(self):
        auth = self._auth
        user = auth.getPrincipalByLogin('srichter')
        annotationsvc = getService(self, 'PrincipalAnnotation')
        annotations = annotationsvc.getAnnotation(user)
        clipboard = getAdapter(annotations, IPrincipalClipboard)
        clipboard.clearContents()
        self.failUnless(clipboard.getContents() == ())

def test_suite():
    t1 = makeSuite(PrincipalClipboardTest)
    return TestSuite((t1,))

if __name__=='__main__':
    main(defaultTest='test_suite')

