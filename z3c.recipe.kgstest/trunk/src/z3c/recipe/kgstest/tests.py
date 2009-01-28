import doctest
import unittest
import zc.buildout.testing


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('z3c.recipe.kgstest', test)

    # need to explicitly name our dependencies for the buildout test environment
    zc.buildout.testing.install('zc.recipe.testrunner', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install('zope.testing', test)
    zc.buildout.testing.install('zope.interface', test)

    zc.buildout.testing.install('zope.dottedname', test)


def tearDown(test):
    zc.buildout.testing.buildoutTearDown(test)


def test_suite():
    ftests = doctest.DocFileSuite('README.txt',
                                 setUp=setUp,
                                 tearDown=tearDown,
                                 optionflags=doctest.ELLIPSIS
                                 | doctest.REPORT_NDIFF
                                 | doctest.NORMALIZE_WHITESPACE)
    suite = unittest.TestSuite()
    suite.addTests(ftests)
    return suite
