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
"""Tests for ComponentConfigURL

$Id: test_componentconfigurl.py,v 1.2 2002/12/25 14:12:38 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.placefulsetup \
     import PlacefulSetup
from zope.app.services.service import ServiceManager
from zope.app.services.service \
     import ServiceConfiguration
from zope.app.traversing import traverse
from zope.publisher.browser import BrowserView
from zope.publisher.browser import TestRequest
from zope.app.browser.services.componentconfigurl import ComponentConfigURL
from zope.security.proxy import Proxy
from zope.security.checker import selectChecker

class V(BrowserView, ComponentConfigURL):
    pass

class C:
    pass

class ContextStub:

    def __init__(self, path):
        self.componentPath = path


class TestComponentConfigURL(PlacefulSetup, TestCase):

    # XXX reduce dependencies on ServiceManager package

    def test_componentURL(self):
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())
        default = traverse(
            self.rootFolder,
            '++etc++Services/Packages/default',
            )
        default.setObject('c', C())
        traverse(default, 'configure').setObject(
            '',
            ServiceConfiguration('test_service',
                                 '/++etc++Services/Packages/default/c')
            )
        config = traverse(default, 'configure/1')
        view = V(config, TestRequest())
        self.assertEqual(view.componentURL(),
                         'http://127.0.0.1/++etc++Services/Packages/default/c')

    def test_componentPath(self):
        context = ContextStub('/path/to/me')
        view = V(context, TestRequest())
        self.assertEqual(view.componentPath(), '/path/to/me')

        context = ContextStub(('', 'path', 'to', 'me'))
        view = V(context, TestRequest())
        self.assertEqual(view.componentPath(), '/path/to/me')

        path = ('', 'path', 'to', 'me')
        wrapped_path = Proxy(path, selectChecker(path))
        context = ContextStub(wrapped_path)
        view = V(context, TestRequest())
        self.assertEqual(view.componentPath(), '/path/to/me')


def test_suite():
    return TestSuite((
        makeSuite(TestComponentConfigURL),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
