##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
"""
$Id$
"""
__docformat__ = 'restructuredtext'

from zc.selenium.pytest import Test
from zope.app.component.hooks import getSite
from zope.app.folder.folder import Folder
from zope.traversing.browser.absoluteurl import absoluteURL
from z3c.configurator import configurator
from zope import event
from zope.lifecycleevent import ObjectCreatedEvent

class SkinTestSuite(Test):

    skin = None

    def setUp(self):
        super(SkinTestSuite, self).setUp()
        self.baseURL = 'http://%s/++skin++%s/seleniumtmp' % \
                       (self.selenium.server, self.skin)

    def reset(self):
        s = self.selenium
        s.open(self.baseURL)

    def sharedSetUp(self):
        super(SkinTestSuite, self).sharedSetUp()
        self.root = getSite()
        configurator.configure(self.root, {},
                               names=['lovely.memcachedclient'])
        if not 'seleniumtmp' in self.root:
            tmp = Folder()
            event.notify(ObjectCreatedEvent(tmp))
            self.tmp = self.root['seleniumtmp'] = tmp
        else:
            self.tmp = self.root['seleniumtmp']

    def sharedTearDown(self):
        #del self.root['seleniumtmp']
        super(SkinTestSuite, self).sharedTearDown()

    def open(self, path):
        self.selenium.open(self.baseURL + path)

    def test_base(self):
        s = self.selenium
        self.reset()
        self.open('/remoteinclude.html')
        s.verifyTextPresent('Remoteinclude Demo')
        s.verifyTextPresent('First Viewlet content')
        s.verifyTextPresent('Second Viewlet content')

class VanillaTestSuite(SkinTestSuite):
    """
    Tests basic view without caching
    """
    skin = 'vanilla'

class ResponseCachedTestSuite(SkinTestSuite):
    """
    Tests views with two cached viewlets
    """
    skin = 'responsecached'

class IncludesTestSuite(SkinTestSuite):
    """
    Tests views with viewlets as includes
    """
    skin = 'includes'

    def test_includes(self):
        s = self.selenium
        self.reset()
        self.open('/remoteinclude.html')
        self.verifyTextPresent(
            '/remoteinclude.html/++manager++IBody/++viewlet++first')
        self.verifyTextPresent(
            '/remoteinclude.html/++manager++IBody/++viewlet++second')
