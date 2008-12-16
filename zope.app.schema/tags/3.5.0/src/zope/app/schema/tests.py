import unittest
from zope.testing import doctest
from zope.app.testing import setup
from zope.app.schema.vocabulary import _clear

def setUp(test):
    setup.placefulSetUp()
    _clear()

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))
