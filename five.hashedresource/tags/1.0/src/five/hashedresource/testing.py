#############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""tests

$Id$
"""
import Products.Five
import Products.Five.browser.resource
import Products.Five.zcml
import Testing.ZopeTestCase
import Testing.ZopeTestCase.layer
import Testing.ZopeTestCase.utils
import five.hashedresource
import five.hashedresource.tests
import os
import os.path
import re
import shutil
import tempfile
import z3c.hashedresource
import zope.app.testing.functional
import zope.interface


class FunctionalTestCase(Testing.ZopeTestCase.FunctionalTestCase):

    zcml = 'ftesting-devmode.zcml'

    def assertMatches(self, regex, text):
        self.assert_(re.match(regex, text), "/%s/ did not match '%s'" % (
            regex, text))

    def setUp(self):
        super(FunctionalTestCase, self).setUp()

        self.tmpdir = tempfile.mkdtemp()
        self.fixture = os.path.join(self.tmpdir, 'fixture')
        os.mkdir(self.fixture)
        open(os.path.join(self.fixture, 'example.txt'), 'w').write('')
        open(os.path.join(self.fixture, 'test.txt'), 'w').write('test\ndata\n')

        for file_ in ['ftesting.zcml', 'ftesting-devmode.zcml']:
            shutil.copy(os.path.join(os.path.dirname(__file__), file_),
                os.path.join(self.tmpdir, file_))

        Products.Five.zcml.load_config(
            'configure.zcml', Products.Five)
        Products.Five.zcml.load_config(
            os.path.join(self.tmpdir, self.zcml))

        self.app = self._app()
        self.request = Testing.ZopeTestCase.utils.makerequest(
            self.app).REQUEST
        zope.interface.directlyProvides(
            self.request, z3c.hashedresource.interfaces.IHashedResourceSkin)

        self.directory = self.app.aq_inner.restrictedTraverse(
            '++resource++myresource')

    def tearDown(self):
        super(FunctionalTestCase, self).tearDown()
        Products.Five.zcml.cleanUp()
        shutil.rmtree(self.tmpdir)

    def _hash(self, text):
        return re.match('http://nohost/\+\+noop\+\+([^/]*)/.*', text).group(1)
