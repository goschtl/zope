import unittest
import os

import zope.testing
import zope.component.testing
import zope.configuration.xmlconfig

import chameleon.core.config
import chameleon.core.testing

import chameleon.html
import chameleon.html.tests
import chameleon.html.language

OPTIONFLAGS = (zope.testing.doctest.ELLIPSIS |
               zope.testing.doctest.NORMALIZE_WHITESPACE)

def render_xss(body, **kwargs):
    parser = chameleon.html.language.XSSTemplateParser()
    return chameleon.core.testing.compile_template(parser, body, **kwargs)

def setUp(suite):
    zope.component.testing.setUp(suite)

def test_suite():
    filesuites = 'language.txt', 'template.txt'
    testsuites = ()
    
    globs = dict(render_xss=render_xss, os=os, path=chameleon.html.tests.__path__[0])
    
    chameleon.core.config.DISK_CACHE = False
    
    return unittest.TestSuite(
        [zope.testing.doctest.DocTestSuite(
        "chameleon.html."+doctest, optionflags=OPTIONFLAGS,
        setUp=setUp, tearDown=zope.component.testing.tearDown) \
         for doctest in testsuites] + 
        
        [zope.testing.doctest.DocFileSuite(
        doctest, optionflags=OPTIONFLAGS,
        globs=globs,
        setUp=setUp, tearDown=zope.component.testing.tearDown,
        package="chameleon.html") for doctest in filesuites]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
