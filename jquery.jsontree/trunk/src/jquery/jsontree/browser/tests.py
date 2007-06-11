##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: layer.py 197 2007-04-13 05:03:32Z rineichen $
"""
__docformat__ = 'restructuredtext'

import unittest

import zope.component
import zope.app.security
from zope.app.component import hooks
from zope.configuration.xmlconfig import XMLConfig
from zope.pagetemplate.tests.util import check_xml
from zope.publisher.browser import TestRequest
from zope.app.component import testing

from z3c.testing import TestCase
from jquery.jsontree.tests import util
from jquery.jsontree.browser import tree


class TestView(tree.SimpleJSONTree):

    def __init__(self, context, request):
        self.context = context
        self.request = request


class TestJSONTreeView(testing.PlacefulSetup, TestCase):

    def setUp(self):
        testing.PlacefulSetup.setUp(self, site=True)
        self.rootFolder.__name__ = 'rootFolder'
        hooks.setSite(self.rootFolder)
        import zope.app.publication
        import zope.app.publisher.browser
        import z3c.template
        import jquery.jsontree
        import zif.jsonserver
        XMLConfig('meta.zcml', zope.component)()
        XMLConfig('meta.zcml', zope.app.security)()
        XMLConfig('meta.zcml', zope.app.publication)()
        XMLConfig('meta.zcml', zope.app.publisher.browser)()
        XMLConfig('meta.zcml', z3c.template)()
        XMLConfig('meta.zcml', zif.jsonserver)()
        XMLConfig('configure.zcml', jquery.jsontree)()

    def test_getTree_folder1(self):
        context = self.rootFolder['folder1']
        request = TestRequest()
        view = TestView(context, request)
        view.update()
        ultree = view.tree
        check_xml(ultree, util.read_output('tree_1.xml'))

    def test_getTree_folder2_1_1(self):
        """This test includes cyrillic letters."""
        context = self.rootFolder['folder2']['folder2_1']['folder2_1_1']
        request = TestRequest()
        view = TestView(context, request)
        view.update()
        ultree = view.tree
        check_xml(ultree, util.read_output('tree_2.xml'))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestJSONTreeView),
        ))


if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
