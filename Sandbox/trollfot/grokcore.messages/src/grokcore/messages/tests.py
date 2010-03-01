# -*- coding: utf-8 -*-
"""Test harness"""

import unittest
import doctest
import os

from zope.app.testing.functional import FunctionalDocFileSuite, ZCMLLayer
import zope.security.management
import zope.publisher.browser


GrokcoreMessageLayer = ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'GrokcoreMessageLayer', allow_teardown=True)


def setUp(test):
    request = zope.publisher.browser.TestRequest()
    zope.security.management.newInteraction()
    interaction = zope.security.management.getInteraction()
    interaction.add(request)

def tearDown(test):
    pass

def test_suite():
    suite = unittest.TestSuite()
    test = FunctionalDocFileSuite('README.txt',
                                  optionflags=doctest.ELLIPSIS,
                                  setUp=setUp,
                                  tearDown=tearDown)
    test.layer = GrokcoreMessageLayer
    suite.addTest(test)
    return suite
