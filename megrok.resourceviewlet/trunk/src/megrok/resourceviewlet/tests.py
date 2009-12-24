# -*- coding: utf-8 -*-

import os.path
import unittest
from zope.app.testing import functional
from zope.testing import doctest, module
from zope.publisher.browser import TestRequest
from zope.app.testing.functional import ZCMLLayer

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer', allow_teardown=True)


def setUp(test):
    module.setUp(test, 'megrok.resourceviewlet.tests')

def tearDown(test):
    module.tearDown(test)

def test_suite():
    suite = unittest.TestSuite()      
    readme = functional.FunctionalDocFileSuite(
        'README.txt', setUp=setUp, tearDown=tearDown)
    readme.layer = FunctionalLayer
    suite.addTest(readme)
    return suite
