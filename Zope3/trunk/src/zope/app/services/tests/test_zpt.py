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
$Id: test_zpt.py,v 1.1 2003/02/07 15:52:22 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
import zope.app.services.zpt

class Test(TestCase):

    # XXX We need tests for the template class itself and for the
    # SearchableText adapter.

    def test_ReadFile(self):
        template = zope.app.services.zpt.ZPTTemplate()
        source = '<p>Test content</p>'
        template.source = source
        adapter = zope.app.services.zpt.ReadFile(template)
        self.assertEqual(adapter.read(), source)
        self.assertEqual(adapter.size(), len(source))

    def test_WriteFile(self):
        template = zope.app.services.zpt.ZPTTemplate()
        source = '<p>Test content</p>'
        template.source = '<p>Old content</p>'
        adapter = zope.app.services.zpt.WriteFile(template)
        adapter.write(source)        
        self.assertEqual(template.source, source)

    def test_ZPTFactory(self):
        factory = zope.app.services.zpt.ZPTFactory(None)
        source = '<p>Test content</p>'
        template = factory('foo', 'text/html', source)
        self.assertEqual(template.source, source)

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))
