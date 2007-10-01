import unittest, os, shutil
from zope.testing import doctest, renormalizing
import zc.buildout.testing
import zc.recipe.egg.tests

def setUp(test):
    zc.recipe.egg.tests.setUp(test)
    zc.buildout.testing.install_develop('z3c.recipe.egg', test)
    shutil.copytree(os.path.join(os.path.dirname(__file__), 'foo'),
                    'foo')
    shutil.copytree(os.path.join(os.path.dirname(__file__), 'bar'),
                    'bar')

def test_suite():
    return doctest.DocFileSuite(
        '../setup.txt',
        '../editable.txt',
        setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
        optionflags=doctest.REPORT_NDIFF,
        checker=renormalizing.RENormalizing([
                zc.buildout.testing.normalize_path,]))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
