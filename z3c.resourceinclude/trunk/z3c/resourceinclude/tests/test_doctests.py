import zope.testing
import unittest

OPTIONFLAGS = (zope.testing.doctest.ELLIPSIS |
               zope.testing.doctest.NORMALIZE_WHITESPACE)

import zope.component
import zope.component.testing
import zope.configuration.xmlconfig

import z3c.pt
import z3c.resourceinclude.testing

def setUp(suite):
    zope.component.testing.setUp(suite)
    z3c.resourceinclude.testing.setSite()
    zope.component.provideAdapter(z3c.resourceinclude.testing.MockSiteURL)
    zope.configuration.xmlconfig.XMLConfig('configure.zcml', z3c.pt)()
    
def test_suite():
    doctests = ('README.txt', 'zcml.txt')

    return unittest.TestSuite(
        [zope.testing.doctest.DocFileSuite(
                doctest,
                optionflags=OPTIONFLAGS,
                setUp=setUp,
                tearDown=zope.component.testing.tearDown,
                package="z3c.resourceinclude") for doctest in doctests]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
