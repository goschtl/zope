import unittest
import doctest
from zope.testing import cleanup

def tearDown(test):
    cleanup.cleanUp()

    # XXX clean up SQLAlchemy?

def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs = {}
    
    suite = unittest.TestSuite()
    
    suite.addTest(doctest.DocFileSuite(
        'README.txt',
        optionflags=optionflags,
        tearDown=tearDown,
        globs=globs))
    return suite
