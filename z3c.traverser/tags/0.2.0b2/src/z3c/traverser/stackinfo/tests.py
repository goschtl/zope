import doctest
import unittest
from zope.testing.doctestunit import DocFileSuite, DocFileSuite
from zope.app.testing import setup
import zope.traversing.testing

def setUp(test):
    root = setup.placefulSetUp(True)
    zope.traversing.testing.setUp()
    test.globs['root'] = root

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    
    return unittest.TestSuite(
        (
        DocFileSuite('README.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
