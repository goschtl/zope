##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Test Local ZPT Templates.

$Id$
"""
import unittest
import zope.interface
from zope.publisher.browser import TestRequest

from zope.app.presentation.zpt import ZPTTemplate, ZPTFactory
from zope.app.presentation.zpt import ReadFile, WriteFile
from zope.app.publisher.browser import BrowserView

# All this just to get zapi.getPath() work :(
from zope.app.testing import ztapi, setup
from zope.app.testing.placelesssetup import PlacelessSetup
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.container.contained import contained


class Data(object):
    pass


class ZPTTemplateTest(unittest.TestCase):

    # TODO: We need tests for the template class itself and for the
    # SearchableText adapter.

    def test_unicode_required(self):
        template = ZPTTemplate()
        self.assertRaises(TypeError, template.setSource, 'not unicode')
        template.source = source = u'123\u1234'
        self.assertEquals(template.source, source)

    def test_ReadFile(self):
        template = ZPTTemplate()
        source = u'<p>Test content</p>'
        template.source = source
        adapter = ReadFile(template)
        self.assertEqual(adapter.read(), source)
        self.assertEqual(adapter.size(), len(source))

    def test_WriteFile(self):
        template = ZPTTemplate()
        source = u'<p>Test content</p>'
        template.source = u'<p>Old content</p>'
        adapter = WriteFile(template)
        adapter.write(source)
        self.assertEqual(template.source, source)

    def test_ZPTFactory(self):
        factory = ZPTFactory(None)
        source = u'<p>Test content</p>'
        template = factory('foo', 'text/html', source)
        self.assertEqual(template.source, source)


class TestDebugFlags(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        setup.setUpTraversal()

    def pageInContext(self, page):
        root = Data()
        zope.interface.directlyProvides(root, IContainmentRoot)
        folder = contained(Data(), root, name='folder')
        return contained(page, folder, name='zpt')

    def test_source_file(self):
        template = ZPTTemplate()
        self.assert_(template.pt_source_file() is None)

        template = self.pageInContext(template)
        self.assertEquals(template.pt_source_file(), '/folder/zpt')

    def test_debug_flags(self):
        template = self.pageInContext(ZPTTemplate())
        template.source = u'<tal:p>Test</tal:p>'

        self.request = TestRequest()
        self.context = None
        self.assertEquals(template.render(self), 'Test\n')

        self.request.debug.showTAL = True
        self.assertEquals(template.render(self), '<tal:p>Test</tal:p>\n')

        self.request.debug.showTAL = False
        self.request.debug.sourceAnnotations = True
        self.assertEquals(template.render(self),
            '<!--\n' +
            '=' * 78 + '\n' +
            '/folder/zpt (line 1)\n' +
            '=' * 78 + '\n' +
            '-->Test\n')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ZPTTemplateTest),
        unittest.makeSuite(TestDebugFlags),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
