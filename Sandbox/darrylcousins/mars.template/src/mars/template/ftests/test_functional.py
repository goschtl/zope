import os
import unittest

from zope.testing import doctest
from zope.app.testing import functional

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
TestLayer = functional.ZCMLLayer(
                       ftesting_zcml, __name__, 'TestLayer')
min_ftesting_zcml = os.path.join(os.path.dirname(__file__), 'minimal_ftesting.zcml')
TestMinimalLayer = functional.ZCMLLayer(
                       min_ftesting_zcml, __name__, 'TestMinimalLayer')

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS
globs = dict(getRootFolder=functional.getRootFolder)

def setUp(test):
    functional.FunctionalTestSetup().setUp()

def tearDown(test):
    functional.FunctionalTestSetup().tearDown()

def test_suite():
    suite = unittest.TestSuite()
    dottedname = 'mars.template.ftests.%s'
    for name in ['template', 'layout']:
        test = doctest.DocTestSuite(
                    dottedname % name, setUp=setUp, globs=globs,
                    tearDown=tearDown, optionflags=optionflags)
        test.layer = TestLayer
        suite.addTest(test)
    test = doctest.DocTestSuite(
                dottedname % 'directive', setUp=setUp, globs=globs,
                tearDown=tearDown, optionflags=optionflags)
    test.layer = TestMinimalLayer
    suite.addTest(test)
    return suite



if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


