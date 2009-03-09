import zope.interface
import zope.component

import os
import unittest
import doctest

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

import zope.component.testing
import zope.configuration.xmlconfig

import z3c.pt
import z3c.ptcompat

class TestParticipation(object):
    principal = 'foobar'
    interaction = None

def setUp(test):
    zope.component.testing.setUp(test)
    zope.configuration.xmlconfig.XMLConfig('meta.zcml', z3c.ptcompat)()
    zope.configuration.xmlconfig.XMLConfig('configure.zcml', z3c.pt)()

def tearDown(test):
    zope.component.testing.tearDown(test)

def test_suite():
    import z3c.ptcompat.tests
    path = z3c.ptcompat.tests.__path__[0]

    globs = dict(
        os=os,
        path=path,
        interface=zope.interface,
        component=zope.component)
    
    return unittest.TestSuite([
        doctest.DocFileSuite(
        "zcml.txt",
        optionflags=OPTIONFLAGS,
        globs=globs,
        setUp=setUp,
        tearDown=tearDown,
        package="z3c.ptcompat")])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
