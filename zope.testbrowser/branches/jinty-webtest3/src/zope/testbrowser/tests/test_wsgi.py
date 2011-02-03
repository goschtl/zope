##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
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

import unittest
from wsgiref.simple_server import demo_app

import zope.testbrowser.wsgi


class SimpleLayer(zope.testbrowser.wsgi.Layer):

    def make_wsgi_app(self):
        return demo_app

SIMPLE_LAYER = SimpleLayer()


class TestWSGILayer(unittest.TestCase):

    def setUp(self):
        # test the layer without depending on zope.testrunner
        SIMPLE_LAYER.setUp()

    def tearDown(self):
        SIMPLE_LAYER.tearDown()

    def test_layer(self):
        """When the layer is setup, the wsgi_app argument is unnecessary"""
        browser = zope.testbrowser.wsgi.Browser()
        browser.open('http://localhost')
        self.assertTrue(browser.contents.startswith('Hello world!\n'))
