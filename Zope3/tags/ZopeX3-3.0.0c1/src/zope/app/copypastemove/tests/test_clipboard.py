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
"""Clipboard tests

$Id$
"""
from unittest import TestCase, TestSuite, main, makeSuite

from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.principalannotation import PrincipalAnnotationService
from zope.app.principalannotation.interfaces import IPrincipalAnnotationService
from zope.app.annotation.interfaces import IAnnotations

from zope.app.copypastemove.interfaces import IPrincipalClipboard
from zope.app.copypastemove import PrincipalClipboard
from zope.app.pluggableauth.tests.authsetup import AuthSetup


class PrincipalClipboardTest(AuthSetup, TestCase):

    def setUp(self):
        AuthSetup.setUp(self)
        self.buildFolders()

        ztapi.provideAdapter(IAnnotations, IPrincipalClipboard,
                             PrincipalClipboard)
        root_sm = zapi.getGlobalServices()
        svc = PrincipalAnnotationService()
        root_sm.defineService("PrincipalAnnotation", \
            IPrincipalAnnotationService)
        root_sm.provideService("PrincipalAnnotation", svc)

    def testAddItems(self):
        user = self._auth['one']['srichter']

        annotationsvc = zapi.getService('PrincipalAnnotation', self)
        annotations = annotationsvc.getAnnotations(user)
        clipboard = IPrincipalClipboard(annotations)
        clipboard.addItems('move', ['bla', 'bla/foo', 'bla/bar'])
        expected = ({'action':'move', 'target':'bla'},
                    {'action':'move', 'target':'bla/foo'},
                    {'action':'move', 'target':'bla/bar'})

        self.failUnless(clipboard.getContents() == expected)
        clipboard.addItems('copy', ['bla'])
        expected = expected + ({'action':'copy', 'target':'bla'},)
        self.failUnless(clipboard.getContents() == expected)

    def testSetContents(self):
        user = self._auth['one']['srichter']

        annotationsvc = zapi.getService('PrincipalAnnotation', self)
        annotations = annotationsvc.getAnnotations(user)
        clipboard = IPrincipalClipboard(annotations)

        expected = ({'action':'move', 'target':'bla'},
                    {'action':'move', 'target':'bla/foo'},
                    {'action':'move', 'target':'bla/bar'})
        clipboard.setContents(expected)
        self.failUnless(clipboard.getContents() == expected)
        clipboard.addItems('copy', ['bla'])
        expected = expected + ({'action':'copy', 'target':'bla'},)
        self.failUnless(clipboard.getContents() == expected)

    def testClearContents(self):
        user = self._auth['one']['srichter']

        annotationsvc = zapi.getService('PrincipalAnnotation', self)
        annotations = annotationsvc.getAnnotations(user)
        clipboard = IPrincipalClipboard(annotations)
        clipboard.clearContents()
        self.failUnless(clipboard.getContents() == ())

def test_suite():
    t1 = makeSuite(PrincipalClipboardTest)
    return TestSuite((t1,))

if __name__=='__main__':
    main(defaultTest='test_suite')

