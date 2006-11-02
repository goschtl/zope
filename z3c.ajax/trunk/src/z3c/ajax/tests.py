import doctest
import unittest
from zope.testing.doctestunit import DocFileSuite, DocTestSuite
from zope.app.testing import setup
from zope import component

def setUp(test):
    setup.placefulSetUp()


def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    
    return unittest.TestSuite(
        (
        DocFileSuite('README.txt',
                     setUp=setUp,tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

