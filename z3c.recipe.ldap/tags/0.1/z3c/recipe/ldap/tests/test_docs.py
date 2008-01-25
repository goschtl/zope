# -*- coding: utf-8 -*-
"""
Generic Test case for 'z3c.recipe.ldap' doctest
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest
import sys
import os

from zope.testing import doctest, renormalizing
import zc.buildout.testing

current_dir = os.path.dirname(__file__)

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('zc.recipe.egg', test)
    zc.buildout.testing.install_develop('z3c.recipe.ldap', test)
    test.globs['openldap'] = os.path.join(
        reduce(lambda path, _: os.path.dirname(path),
               range(5), __file__),
        'parts', 'openldap')

def doc_suite(test_dir, setUp=setUp,
              tearDown=zc.buildout.testing.buildoutTearDown,
              globs=None):
    """Returns a test suite, based on doctests found in /doctest."""
    if globs is None:
        globs = globals()

    globs['test_dir'] = current_dir
    
    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

    package_dir = os.path.split(test_dir)[0]
    if package_dir not in sys.path:
        sys.path.append(package_dir)

    doctest_dir = os.path.join(package_dir, 'docs')

    # filtering files on extension
    docs = [os.path.join(doctest_dir, doc) for doc in
            os.listdir(doctest_dir) if doc.endswith('.txt')]

    return unittest.TestSuite(
        doctest.DocFileSuite(
            test, optionflags=flags, globs=globs, setUp=setUp,
            tearDown=tearDown, module_relative=False,
            checker=renormalizing.RENormalizing([
                zc.buildout.testing.normalize_path]))
        for test in docs)

def test_suite():
    """returns the test suite"""
    return doc_suite(current_dir)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

