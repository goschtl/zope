import unittest
import doctest
from zope.testing import cleanup
from zope.testing import module
import zope.component.eventtesting
from zope import component
from megrok import layout

    
def moduleSetUp(test):
    module.setUp(test, '__main__')
    
def moduleTearDown(test):    
    module.tearDown(test)
    cleanup.cleanUp()
    
def zopeSetUp(test):
    zope.component.eventtesting.setUp(test)

def zopeTearDown(test):
    cleanup.cleanUp()
    
def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs = {}
    suite = unittest.TestSuite()
    
    suite.addTest(
        doctest.DocFileSuite(
            '../README.txt',
            optionflags=optionflags,
            setUp=moduleSetUp,
            tearDown=moduleTearDown,
            globs=globs)
        )

    return suite
