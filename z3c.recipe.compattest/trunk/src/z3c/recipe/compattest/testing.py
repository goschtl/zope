import doctest
import unittest
import zc.buildout.testing


def DocFileSuite(*args, **kw):
    def setUp(test):
        zc.buildout.testing.buildoutSetUp(test)
        zc.buildout.testing.install_develop('z3c.recipe.compattest', test)

        # need to explicitly name our dependencies for the buildout test
        # environment
        zc.buildout.testing.install('zc.recipe.testrunner', test)
        zc.buildout.testing.install('zc.recipe.egg', test)
        zc.buildout.testing.install('zope.testing', test)
        zc.buildout.testing.install('zope.interface', test)
        zc.buildout.testing.install('zope.exceptions', test)

        zc.buildout.testing.install('infrae.subversion', test)
        zc.buildout.testing.install('py', test)
        zc.buildout.testing.install('zope.dottedname', test)

    def tearDown(test):
        zc.buildout.testing.buildoutTearDown(test)

    kw['setUp'] = setUp
    kw['tearDown'] = tearDown
    kw['optionflags'] = (doctest.ELLIPSIS
                         | doctest.REPORT_NDIFF
                         | doctest.NORMALIZE_WHITESPACE)

    return doctest.DocFileSuite(*args, **kw)
