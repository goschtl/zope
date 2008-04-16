import unittest
from zope.testing import doctest, cleanup

from zope.configuration import xmlconfig

import z3c.metrics
from z3c.metrics import bbb

def setUp(test):
    cleanup.setUp()
    bbb.eventtesting.PlacelessSetup().setUp()
    xmlconfig.file('testing.zcml', z3c.metrics)

def tearDown(test):
    cleanup.tearDown()

def test_suite():
    return doctest.DocFileSuite(
        'scale.txt',
        'index.txt',
        'verify.txt',
        'event.txt',
        'dispatch.txt',
        'meta.txt',
        'README.txt',
        setUp=setUp, tearDown=tearDown,
        optionflags=(
            doctest.REPORT_NDIFF|
            #doctest.REPORT_ONLY_FIRST_FAILURE|
            doctest.NORMALIZE_WHITESPACE|
            doctest.ELLIPSIS))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
