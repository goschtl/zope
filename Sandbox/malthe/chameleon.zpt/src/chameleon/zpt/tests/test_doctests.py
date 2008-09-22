import zope.testing
import unittest

OPTIONFLAGS = (zope.testing.doctest.ELLIPSIS |
               zope.testing.doctest.NORMALIZE_WHITESPACE)

import zope.component.testing
import zope.configuration.xmlconfig

import chameleon.core.config
import chameleon.core.testing

import chameleon.zpt
import chameleon.zpt.language

def render_template(body, **kwargs):
    parser = chameleon.zpt.language.Parser()
    return chameleon.core.testing.compile_template(parser, body, **kwargs)

def setUp(suite):
    zope.component.testing.setUp(suite)
    zope.configuration.xmlconfig.XMLConfig('configure.zcml', chameleon.zpt)()

def test_suite():
    filesuites = 'language.txt', 'template.txt', 'i18n.txt'
    testsuites = 'language', 'expressions'

    globs = dict(render=render_template)
    
    chameleon.core.config.DISK_CACHE = False
    
    return unittest.TestSuite(
        [zope.testing.doctest.DocTestSuite(
        "chameleon.zpt."+doctest, optionflags=OPTIONFLAGS,
        setUp=setUp, tearDown=zope.component.testing.tearDown) \
         for doctest in testsuites] + 
        
        [zope.testing.doctest.DocFileSuite(
        doctest, optionflags=OPTIONFLAGS,
        globs=globs,
        setUp=setUp, tearDown=zope.component.testing.tearDown,
        package="chameleon.zpt") for doctest in filesuites]
        )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
