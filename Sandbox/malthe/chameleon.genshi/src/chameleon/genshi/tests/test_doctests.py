import zope.testing
import unittest

OPTIONFLAGS = (zope.testing.doctest.ELLIPSIS |
               zope.testing.doctest.NORMALIZE_WHITESPACE)

import zope.component.testing

import chameleon.core.config
import chameleon.core.testing

import chameleon.genshi
import chameleon.genshi.language

def render_template(body, **kwargs):
    parser = chameleon.genshi.language.Parser()
    return chameleon.core.testing.compile_template(parser, body, **kwargs)

def setUp(suite):
    zope.component.testing.setUp(suite)

def test_suite():
    filesuites = 'language.txt', 'template.txt'
    testsuites = 'language', 'expressions'

    globs = dict(render=render_template)
    
    chameleon.core.config.DISK_CACHE = False
    
    return unittest.TestSuite(
        [zope.testing.doctest.DocTestSuite(
        "chameleon.genshi."+doctest, optionflags=OPTIONFLAGS,
        setUp=setUp, tearDown=zope.component.testing.tearDown) \
         for doctest in testsuites] + 
        
        [zope.testing.doctest.DocFileSuite(
        doctest, optionflags=OPTIONFLAGS,
        globs=globs,
        setUp=setUp, tearDown=zope.component.testing.tearDown,
        package="chameleon.genshi") for doctest in filesuites]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
