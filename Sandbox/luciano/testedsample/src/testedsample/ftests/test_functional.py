import os
import unittest
import testedsample
from zope.testing import doctest
from zope.app.testing.functional import (FunctionalTestSetup, ZCMLLayer,
                                         getRootFolder, FunctionalDocFileSuite)
import zope.testbrowser.browser
import zope.testbrowser.testing

ftesting_zcml = os.path.join(os.path.dirname(testedsample.__file__), 'ftesting.zcml')
TestedSampleFunctionalLayer = ZCMLLayer(ftesting_zcml, __name__, 'TestedSampleFunctionalLayer')

def test_suite():
    suite = unittest.TestSuite()
    docfiles = ['index.txt']

    for docfile in docfiles:
        test = FunctionalDocFileSuite(
             docfile,
             globs=dict(getRootFolder=getRootFolder, Browser=zope.testbrowser.testing.Browser),
             optionflags = (doctest.ELLIPSIS
                            | doctest.REPORT_NDIFF
                            | doctest.NORMALIZE_WHITESPACE),)
        test.layer = TestedSampleFunctionalLayer
        suite.addTest(test)

    return suite

if __name__ == '__main__':
    unittest.main()

