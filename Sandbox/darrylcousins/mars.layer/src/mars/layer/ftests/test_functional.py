import unittest
from zope.testing import doctest

from zope.app.testing.functional import FunctionalTestSetup, getRootFolder
from zope.app.testing import functional
functional.defineLayer('TestMinimalLayer', 'minimal-ftesting.zcml')
functional.defineLayer('TestPageletLayer', 'pagelet-ftesting.zcml')

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS
globs = dict(getRootFolder=getRootFolder)

def setUp(test):
    FunctionalTestSetup().setUp()

def tearDown(test):
    FunctionalTestSetup().tearDown()

def test_suite():
    suite = unittest.TestSuite()
    dottedname = 'mars.layer.ftests.%s'
    for name in ['minimal', 'directive']:
        test = doctest.DocTestSuite(
                    dottedname % name, setUp=setUp, globs=globs,
                    tearDown=tearDown, optionflags=optionflags)
        test.layer = TestMinimalLayer
        suite.addTest(test)
    test = doctest.DocTestSuite(
                dottedname % 'pagelet', setUp=setUp, globs=globs,
                tearDown=tearDown, optionflags=optionflags)
    test.layer = TestPageletLayer
    suite.addTest(test)
    return suite



if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


