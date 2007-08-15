import os
import unittest
from zope.testing import doctest
from zope.app.testing import setup
from zope.app.testing.functional import ZCMLLayer

from zope.app.testing.functional import FunctionalTestSetup, getRootFolder

import tfws.website

ftesting_zcml = os.path.join(
    os.path.dirname(tfws.website.__file__), 'ftesting.zcml')

TestLayer = ZCMLLayer(ftesting_zcml, __name__, 'TestLayer')
SeleniumTestLayer = ZCMLLayer(ftesting_zcml, __name__, 'SeleniumLayer')

optionflags = doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS
globs = dict(getRootFolder=getRootFolder)

def setUp(test):
    FunctionalTestSetup().setUp()

def tearDown(test):
    FunctionalTestSetup().tearDown()

def test_suite():
    suite = unittest.TestSuite()
    test = doctest.DocFileSuite(
                '../BROWSER.txt', setUp=setUp, globs=globs,
                tearDown=tearDown, optionflags=optionflags)
    test.layer = TestLayer
    seleniumtest = doctest.DocFileSuite(
                '../selenium.txt', setUp=setUp, globs=globs,
                tearDown=tearDown, optionflags=optionflags)
    seleniumtest.layer = SeleniumTestLayer
    suite.addTest(seleniumtest)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
