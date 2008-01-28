import unittest
import os.path
import grok

from zope.testing import doctest
from zope.app.testing.functional import (
    HTTPCaller, getRootFolder, FunctionalTestSetup,
    sync, ZCMLLayer, FunctionalDocFileSuite)

DOCTESTFILES = ['browser.txt']

ftesting_zcml = os.path.join(os.path.dirname(grok.__file__),
                             'ftesting.zcml')
GrokIMDBFunctionalLayer = ZCMLLayer(ftesting_zcml, __name__,
                                    'GrokIMDBFunctionalLayer')

def setUp(test):
    FunctionalTestSetup().setUp()

def tearDown(test):
    FunctionalTestSetup().tearDown()

def suiteFromFile(name):
    suite = unittest.TestSuite()
    test = FunctionalDocFileSuite(
        name, setUp=setUp, tearDown=tearDown,
        encoding='utf-8',
        globs=dict(http=HTTPCaller(),
                   getRootFolder=getRootFolder,
                   sync=sync
                   ),
        optionflags = (doctest.ELLIPSIS+
                       doctest.NORMALIZE_WHITESPACE+
                       doctest.REPORT_NDIFF)
        )
    test.layer = GrokIMDBFunctionalLayer
    suite.addTest(test)
    return suite

def test_suite():
    suite = unittest.TestSuite()
    for name in DOCTESTFILES:
        suite.addTest(suiteFromFile(name))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
