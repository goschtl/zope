import unittest
from zope.testing import doctest, cleanup
import grokimdb

DOCTESTFILES = ['app.py', 'grokimdb.txt']

def setUpZope(test):
    pass

def cleanUpZope(test):
    cleanup.cleanUp()

def test_suite():
    suite = unittest.TestSuite()
    for name in DOCTESTFILES:
        suite.addTest(doctest.DocFileSuite(
            name,
            package=grokimdb,
            setUp=setUpZope,
            tearDown=cleanUpZope,
            encoding='utf8',
            optionflags=doctest.ELLIPSIS+
            doctest.NORMALIZE_WHITESPACE)
        )
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
