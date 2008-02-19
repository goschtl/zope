import os
import unittest
import simpleauthtest
from zope.testing import doctest
from zope.app.testing.functional import (FunctionalTestSetup, ZCMLLayer,
                                         getRootFolder, FunctionalDocFileSuite)
import zope.testbrowser.browser
import zope.testbrowser.testing

ftesting_zcml = os.path.join(os.path.dirname(simpleauthtest.__file__), 'ftesting.zcml')
SimpleAuthFunctionalLayer = ZCMLLayer(ftesting_zcml, __name__, 'SimpleAuthFunctionalLayer')

def test_suite():
    suite = unittest.TestSuite()
    docfiles = ['index.txt',]

    for docfile in docfiles:
        test = FunctionalDocFileSuite(
             docfile,
             globs=dict(getRootFolder=getRootFolder, Browser=zope.testbrowser.testing.Browser),
             optionflags = (doctest.ELLIPSIS
                            | doctest.REPORT_NDIFF
                            | doctest.NORMALIZE_WHITESPACE),)
        test.layer = SimpleAuthFunctionalLayer
        suite.addTest(test)

    return suite

if __name__ == '__main__':
    unittest.main()

