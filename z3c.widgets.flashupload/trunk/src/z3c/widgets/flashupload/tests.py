import doctest
import unittest
from zope.testing.doctestunit import DocTestSuite, DocFileSuite
from zope.app.testing import setup

def setUp(test):
    setup.placefulSetUp()

def tearDown(test):
    setup.placefulTearDown()

def test_suite():

    return unittest.TestSuite(
        (
        DocTestSuite('z3c.widgets.flashupload.ticket',
                     setUp=setUp,tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('README.txt',
                     setUp=setUp,tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),

        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

