from zope import interface
from zope import component
from zope import schema

import zope.testing
import unittest

OPTIONFLAGS = (zope.testing.doctest.REPORT_ONLY_FIRST_FAILURE |
               zope.testing.doctest.ELLIPSIS |
               zope.testing.doctest.NORMALIZE_WHITESPACE)

import zope.component.testing

def test_suite():
    doctests = ('README.txt',)

    globs = dict(interface=interface, component=component, schema=schema)
    
    return unittest.TestSuite((
        zope.testing.doctest.DocFileSuite(doctest,
                                          optionflags=OPTIONFLAGS,
                                          setUp=zope.component.testing.setUp,
                                          tearDown=zope.component.testing.tearDown,
                                          globs=globs,
                                          package="z3c.schemadiff") for doctest in doctests
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
