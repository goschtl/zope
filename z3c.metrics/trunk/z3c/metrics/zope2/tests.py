import unittest
from zope.testing import doctest, cleanup

from Testing import ZopeTestCase

from zope.configuration import xmlconfig

import z3c.metrics.zope2

def setUp(test):
    cleanup.setUp()
    xmlconfig.file('testing.zcml', z3c.metrics.zope2)

def tearDown(test):
    cleanup.tearDown()

def test_suite():
    return ZopeTestCase.ZopeDocFileSuite(
        'catalog.txt',
        setUp=setUp, tearDown=tearDown,
        optionflags=(
            doctest.REPORT_NDIFF|
            #doctest.REPORT_ONLY_FIRST_FAILURE|
            doctest.NORMALIZE_WHITESPACE|
            doctest.ELLIPSIS))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
