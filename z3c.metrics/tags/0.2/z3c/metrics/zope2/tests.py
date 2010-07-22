import unittest
from zope.testing import doctest, cleanup

try:
    from Testing import ZopeTestCase
except ImportError:
    have_zope2 = False
else:
    have_zope2 = True

from zope.configuration import xmlconfig

import z3c.metrics.zope2


def setUp(test):
    cleanup.setUp()
    xmlconfig.file('testing.zcml', z3c.metrics.zope2)


def tearDown(test):
    cleanup.tearDown()


if have_zope2:
    def test_suite():
        return ZopeTestCase.ZopeDocFileSuite(
            'catalog.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=(
                doctest.REPORT_NDIFF |
                #doctest.REPORT_ONLY_FIRST_FAILURE |
                doctest.NORMALIZE_WHITESPACE |
                doctest.ELLIPSIS))
else:
    def test_suite():
        return unittest.TestSuite()
