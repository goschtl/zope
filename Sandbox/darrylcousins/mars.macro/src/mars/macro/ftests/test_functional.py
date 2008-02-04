import os
import unittest
from zope.testing import doctest

from zope.app.testing import functional

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
TestLayer = functional.ZCMLLayer(
                       ftesting_zcml, __name__, 'TestLayer')

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS
globs = dict(getRootFolder=functional.getRootFolder)

def setUp(test):
    functional.FunctionalTestSetup().setUp()

def tearDown(test):
    functional.FunctionalTestSetup().tearDown()

def test_suite():
    suite = unittest.TestSuite()
    dottedname = 'mars.macro.ftests.%s'
    for name in ['macro', 'directive']:
        test = doctest.DocTestSuite(
                    dottedname % name, setUp=setUp, globs=globs,
                    tearDown=tearDown, optionflags=optionflags)
        test.layer = TestLayer
        suite.addTest(test)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
