import unittest
from zope.testing import doctest

from zope.app.testing.functional import FunctionalTestSetup, getRootFolder
from zope.app.testing import functional
functional.defineLayer('TestLayer', 'ftesting.zcml')

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS
globs = dict(getRootFolder=getRootFolder)

def setUp(test):
    FunctionalTestSetup().setUp()

def tearDown(test):
    FunctionalTestSetup().tearDown()

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
