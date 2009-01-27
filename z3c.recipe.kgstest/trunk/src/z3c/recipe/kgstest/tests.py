import doctest
import zc.buildout.testing


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('z3c.recipe.kgstest', test)


def tearDown(test):
    zc.buildout.testing.buildoutTearDown(test)


def test_suite():
    return doctest.DocFileSuite('README.txt',
                                setUp=setUp,
                                tearDown=tearDown,
                                optionflags=doctest.ELLIPSIS
                                | doctest.REPORT_NDIFF
                                | doctest.NORMALIZE_WHITESPACE)

