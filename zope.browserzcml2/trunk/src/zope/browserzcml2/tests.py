##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
"""Tests

$Id$
"""
import unittest
import zope.browserzcml2
import zope.component.testing
import zope.app.publisher.browser
from zope.testing import doctest, module
from zope.configuration import xmlconfig
from zope.traversing.adapters import DefaultTraversable

__docformat__ = "reStructuredText"

def run_config(snippet):
    global _context
    template = """\
    <configure
        xmlns="http://namespaces.zope.org/zope"
        xmlns:browser="http://namespaces.zope.org/browser"
        xmlns:browser2="http://namespaces.zope.org/browser2"
        >
        %s
    </configure>"""
    xmlconfig.string(template % snippet, _context)

_context = None
def setUp(test):
    test.globs['run_config'] = run_config
    module.setUp(test, 'zope.browserzcml2.README')
    zope.component.testing.setUp(test)

    global _context
    _context = xmlconfig.file('meta.zcml', zope.browserzcml2)
    xmlconfig.file('meta.zcml', zope.app.publisher.browser, _context)

    zope.component.provideAdapter(DefaultTraversable, (None,))

def tearDown(test):
    global _context
    _context = None
    module.tearDown(test)
    zope.component.testing.tearDown(test)

def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite('README.txt', setUp=setUp, tearDown=tearDown)
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
