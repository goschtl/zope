from zope import interface
from zope import component

import zope.testing
import unittest

OPTIONFLAGS = (zope.testing.doctest.REPORT_ONLY_FIRST_FAILURE |
               zope.testing.doctest.ELLIPSIS |
               zope.testing.doctest.NORMALIZE_WHITESPACE)

import zope.component.testing

def test_suite():
    doctests = ('README.txt', 'zcml.txt', 'utils.py', 'browser/insertion.py')

    import z3c.layout.tests
    path = z3c.layout.tests.__path__[0]

    globs = dict(
        interface=interface,
        component=component,
        test_path=path)
    
    return unittest.TestSuite((
        zope.testing.doctest.DocFileSuite(doctest,
                                          optionflags=OPTIONFLAGS,
                                          setUp=zope.component.testing.setUp,
                                          tearDown=zope.component.testing.tearDown,
                                          globs=globs,
                                          package="z3c.layout") for doctest in doctests
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
