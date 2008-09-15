import zope.testing
import unittest

OPTIONFLAGS = (zope.testing.doctest.ELLIPSIS |
               zope.testing.doctest.NORMALIZE_WHITESPACE)

import zope.component.testing

import chameleon.core.config

def setUp(suite):
    zope.component.testing.setUp(suite)
    
def test_suite():
    filesuites = 'template.txt', 'codegen.txt', 'translation.txt'
    testsuites = 'translation', 'clauses', 'expressions'

    chameleon.core.config.DISK_CACHE = False
    
    return unittest.TestSuite(
        [zope.testing.doctest.DocTestSuite(
        "chameleon.core."+doctest, optionflags=OPTIONFLAGS,
        setUp=setUp, tearDown=zope.component.testing.tearDown) \
         for doctest in testsuites] + 
        
        [zope.testing.doctest.DocFileSuite(
        doctest, optionflags=OPTIONFLAGS,
        setUp=setUp, tearDown=zope.component.testing.tearDown,
        package="chameleon.core") for doctest in filesuites]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
