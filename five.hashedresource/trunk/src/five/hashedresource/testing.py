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


fixture = os.path.join(
    os.path.dirname(five.hashedresource.tests.__file__), 'fixture')


class HashedResourcesLayer(Testing.ZopeTestCase.layer.ZopeLiteLayer):

    @classmethod
    def setUp(cls):
        open(os.path.join(fixture, 'example.txt'), 'w').write('')
        Products.Five.zcml.load_config(
            'configure.zcml', Products.Five)
        Products.Five.zcml.load_config(
            'ftesting-devmode.zcml', five.hashedresource)

    @classmethod
    def tearDown(cls):
        os.unlink(os.path.join(fixture, 'example.txt'))


class FunctionalTestCase(Testing.ZopeTestCase.FunctionalTestCase):

    layer = HashedResourcesLayer

    def assertMatches(self, regex, text):
        self.assert_(re.match(regex, text), "/%s/ did not match '%s'" % (
            regex, text))

    def setUp(self):
        super(FunctionalTestCase, self).setUp()

        self.tmpdir = tempfile.mkdtemp()
        open(os.path.join(self.tmpdir, 'example.txt'), 'w').write('')
        self.dirname = os.path.basename(self.tmpdir)

        self.app = self._app()
        self.request = Testing.ZopeTestCase.utils.makerequest(
            self.app).REQUEST
        zope.interface.directlyProvides(
            self.request, z3c.hashedresource.interfaces.IHashedResourceSkin)

        self.directory = self.app.aq_inner.restrictedTraverse(
            '++resource++myresource')

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _hash(self, text):
        return re.match('http://nohost/\+\+noop\+\+([^/]*)/.*', text).group(1)
