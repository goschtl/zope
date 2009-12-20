# -*- coding: utf-8 -*-

import unittest
from zope.app.testing import functional
from zope.testing import doctest, module
from zope.publisher.browser import TestRequest
from megrok.resource.ftests import FunctionalLayer


def setUp(test):
    module.setUp(test, 'megrok.resource.ftests')

def tearDown(test):
    module.tearDown(test)

def test_suite():
    suite = unittest.TestSuite()      
    readme = functional.FunctionalDocFileSuite(
        '../README.txt', setUp=setUp, tearDown=tearDown)
    readme.layer = FunctionalLayer
    suite.addTest(readme)
    return suite
