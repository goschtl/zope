import unittest
import doctest
import tempfile
import os
import sys
from contextlib import contextmanager
from pkg_resources import working_set, resource_filename

from zc.buildout.easy_install import install
from zc.buildout import testing


@contextmanager
def pwd(directory):
    before = os.getcwd()
    os.chdir(directory)
    yield
    os.chdir(before)


def setUp(test):
    test.target_dir = tempfile.mkdtemp('hurry.resource.test-installs')

    # Inspired by the test setup from z3c.autoinclude.
    project_dir = resource_filename('hurry.resource', 'testdata/MyPackage')
    dist_dir = os.path.join(project_dir, 'dist')

    if os.path.isdir(dist_dir):
        testing.rmdir(dist_dir)

    with pwd(project_dir):
        testing.system('%s setup.py sdist' % (sys.executable))

    new_working_set = install(['mypackage'],
                              test.target_dir,
                              links=[dist_dir],
                              working_set=working_set)

    # we must perform a magical incantation on each distribution
    for dist in new_working_set:
        dist.activate()


def tearDown(test):
    testing.remove(test.target_dir)


def test_suite():
    readme = doctest.DocFileSuite(
        'README.txt',
        setUp=setUp,
        tearDown=tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS)
    return unittest.TestSuite([readme])
