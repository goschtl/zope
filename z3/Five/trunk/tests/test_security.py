import os, sys
from os import curdir
from os.path import join, abspath, dirname, split

try:
    __file__
except NameError:
    # Test was called directly, so no __file__ global exists.
    _prefix = abspath(curdir)
else:
    # Test was called by another test.
    _prefix = abspath(dirname(__file__))

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# XXX hack but no other way to initialize options apparently
from Zope.Startup.run import configure
configure(join(_prefix, '..', '..', '..', 'etc', 'zope.conf'))

import unittest
from Testing import ZopeTestCase

ZopeTestCase.installProduct('Five')

from AccessControl import ClassSecurityInfo

class Dummy:

    def foo(self): pass
    def bar(self): pass
    def baz(self): pass
    def keg(self): pass
    def wot(self): pass

class Dummy1(Dummy):

    security = ClassSecurityInfo()
    security.declareProtected('View', 'foo')

class Dummy2(Dummy):

    security = ClassSecurityInfo()
    security.declarePublic('foo')
    security.declareProtected('View', 'bar')
    security.declarePrivate('baz')
    security.declareProtected('Edit', 'keg')


class SecurityTestCase(ZopeTestCase.ZopeTestCase):

    def test_require(self):
        # Need to use xmlconfig() to run a
        # small zcml snippet and then check
        # the class __ac_permissions__ to see
        # if the declaration took effect.
        pass

    def test_allow(self):
        pass

    def test_initialize(self):
        pass


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SecurityTestCase))
    return suite

if __name__ == '__main__':
    framework()

