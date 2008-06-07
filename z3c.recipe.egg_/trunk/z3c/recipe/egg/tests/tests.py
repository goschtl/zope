import unittest, os, shutil, tempfile
from zope.testing import doctest, renormalizing
import zc.buildout.testing
from zc.recipe.egg import tests

versioned_dist_template = """
from setuptools import setup
setup(name=%r, zip_safe=False, version=%r,
      author='bob', url='bob', author_email='bob')
"""

def create_sample_egg(dest, template=versioned_dist_template,
                      name='demoupgraded', version='1.0'):
    write = zc.buildout.testing.write
    tmp = tempfile.mkdtemp()
    try:
        write(tmp, 'README.txt', '')
        write(tmp, 'setup.py', template % (name, version))
        zc.buildout.testing.sdist(tmp, dest)
    finally:
        shutil.rmtree(tmp)

def setUp(test):
    tests.setUp(test)
    zc.buildout.testing.install_develop('z3c.recipe.egg', test)
    shutil.copytree(os.path.join(os.path.dirname(__file__), 'foo'),
                    'foo')
    shutil.copytree(os.path.join(os.path.dirname(__file__), 'bar'),
                    'bar')
    create_sample_egg(test.globs['sample_eggs'])

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
