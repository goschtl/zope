import unittest
from zope.testing import doctest
from zope.configuration import xmlconfig

import megrok.kss.tests
from megrok.kss.testing import IntegrationLayer


def setUp(test):
    """docstring for setUp"""
    xmlconfig.file('configure.zcml', package=megrok.kss.tests)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite('megrok.kss.tests.kss',
                                        optionflags=doctest.NORMALIZE_WHITESPACE))
    suite.layer = IntegrationLayer
    return suite
