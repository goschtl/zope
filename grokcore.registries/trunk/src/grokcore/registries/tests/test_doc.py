import doctest
import unittest
from zope.app.testing import placelesssetup, setup

def setUp(test):
    placelesssetup.setUp(test)
    setup.setUpTestAsModule(test, name='README')

def tearDown(test):
    placelesssetup.tearDown(test)

def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                '../README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
            ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
