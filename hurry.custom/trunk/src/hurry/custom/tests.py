import unittest
import doctest

from zope.testing import cleanup
import zope.component.eventtesting

from hurry.custom.testing import setHooks, setSite, getSite, DummySite

def setUpReadMe(test):
    # set up special local component architecture
    setHooks()
    # set up event handling
    zope.component.eventtesting.setUp(test)

def tearDownReadMe(test):
    # clean up Zope
    cleanup.cleanUp()

def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs = {
        'DummySite': DummySite,
        'setSite': setSite,
        'getSite': getSite,
        }
    
    suite = unittest.TestSuite()
    
    suite.addTest(doctest.DocFileSuite(
        'README.txt',
        optionflags=optionflags,
        setUp=setUpReadMe,
        tearDown=tearDownReadMe,
        globs=globs))
    return suite
