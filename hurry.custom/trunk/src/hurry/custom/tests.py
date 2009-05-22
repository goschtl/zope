import unittest
import doctest

from hurry import custom

from zope.testing import cleanup
import zope.component.eventtesting
from zope.configuration.xmlconfig import XMLConfig

from hurry.custom.testing import setHooks, setSite, getSite, DummySite

def setUpCustom(test):
    # set up special local component architecture
    setHooks()
    
    # set up event handling
    zope.component.eventtesting.setUp(test)

    # set up the directives
    XMLConfig('meta.zcml', custom)()

def tearDownCustom(test):
    # clean up Zope
    cleanup.cleanUp()
    setSite(None)

def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    globs = {
        'DummySite': DummySite,
        'setSite': setSite,
        'getSite': getSite,
        }
    
    suite = unittest.TestSuite()
    
    suite.addTest(doctest.DocFileSuite(
        'README.txt', 'jsontemplate.txt', 'zcml.txt',
        optionflags=optionflags,
        setUp=setUpCustom,
        tearDown=tearDownCustom,
        globs=globs))
    
    return suite
