import unittest
import doctest
import os

import zope.interface
import zope.component
import zope.component.testing
import zope.configuration.xmlconfig

import chameleon.core.config
import chameleon.core.testing

import chameleon.html
import chameleon.html.tests
import chameleon.html.language


OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def render_xss(body, **kwargs):
    parser = chameleon.html.language.XSSTemplateParser()
    return chameleon.core.testing.compile_template(parser, body, **kwargs)

def setUp(suite):
    zope.component.testing.setUp(suite)

def test_suite():
    filesuites = 'language.txt', 'template.txt'
    testsuites = ()
    
    globs = dict(
        render_xss=render_xss,
        interface=zope.interface,
        component=zope.component,
        os=os,
        path=chameleon.html.tests.__path__[0])
    
    chameleon.core.config.DISK_CACHE = False
    
    return unittest.TestSuite(
        [doctest.DocTestSuite(
        "chameleon.html."+dt, optionflags=OPTIONFLAGS,
        setUp=setUp, tearDown=zope.component.testing.tearDown) \
         for dt in testsuites] + 
        
        [doctest.DocFileSuite(
        dt, optionflags=OPTIONFLAGS,
        globs=globs,
        setUp=setUp, tearDown=zope.component.testing.tearDown,
        package="chameleon.html") for dt in filesuites]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
