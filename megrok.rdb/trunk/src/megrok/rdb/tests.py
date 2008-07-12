import unittest
import doctest
from zope.testing import cleanup
from zope.testing import module

def setUp(test):
    # using zope.testing.module.setUp to work around
    # __module__ being '__builtin__' by default
    module.setUp(test, '__main__')
    
def tearDown(test):
    module.tearDown(test)
    cleanup.cleanUp()

    # XXX clean up SQLAlchemy?

def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs = {}
    
    suite = unittest.TestSuite()
    
    suite.addTest(doctest.DocFileSuite(
            'README.txt',
            optionflags=optionflags,
            setUp=setUp,
            tearDown=tearDown,
            globs=globs))
    suite.addTest(doctest.DocFileSuite(
            'schema.txt',
            optionflags=optionflags,
            ))
    return suite
