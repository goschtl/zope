##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
$Id$
"""
from unittest import TestCase, TestSuite, makeSuite
from zope.app.presentation.zpt import ZPTTemplate, ZPTFactory
from zope.app.presentation.zpt import ReadFile, WriteFile
from zope.publisher.browser import TestRequest
from zope.app.publisher.browser import BrowserView

class Test(TestCase):

    # XXX We need tests for the template class itself and for the
    # SearchableText adapter.

    def test_ReadFile(self):
        template = ZPTTemplate()
        source = '<p>Test content</p>'
        template.source = source
        adapter = ReadFile(template)
        self.assertEqual(adapter.read(), source)
        self.assertEqual(adapter.size(), len(source))

    def test_WriteFile(self):
        template = ZPTTemplate()
        source = '<p>Test content</p>'
        template.source = '<p>Old content</p>'
        adapter = WriteFile(template)
        adapter.write(source)        
        self.assertEqual(template.source, source)

    def test_ZPTFactory(self):
        factory = ZPTFactory(None)
        source = '<p>Test content</p>'
        template = factory('foo', 'text/html', source)
        self.assertEqual(template.source, source)
                           

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))
