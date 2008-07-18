##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import logging
import os
import os.path
import pprint
import re
import zc.buildout.buildout
import zc.buildout.testing
import zc.buildout.tests
import StringIO
import sys

import unittest
import zc.recipe.egg
import zc.recipe.macro
import zc.recipe.testrunner
import zope.testing
import zope.testing.doctest
import zope.testing.renormalizing


here = os.path.abspath(os.path.dirname(__file__))

def buildout_pprint(buildout):
    b_dict = dict((key, dict(value)) for (key, value) in buildout.iteritems())
    string = pprint.pformat(b_dict).replace('\\n', '\n')
    print string

def setupBuildout(test, *args):
    tmpdir, rmdir, write, sample_buildout = (
        test.globs['tmpdir'],
        test.globs['rmdir'],
        test.globs['write'],
        test.globs['sample_buildout'],)

    args = list(args)
    cfg = args.pop()
    filename = args.pop()
    directory = os.path.join(*args)
    eggs = os.path.join(os.path.join(directory, 'eggs'))
    path = os.path.join(directory, filename)
    rmdir(directory)
    test.globs['sample_buildout'] = sample_buildout = tmpdir(sample_buildout)
    write(path, cfg)
    os.chdir(sample_buildout)
    buildout = zc.buildout.buildout.Buildout(
        path,
        [# trick bootstrap into putting the buildout develop egg
         # in the eggs dir.
         ('buildout', 'develop-eggs-directory', 'eggs'),
         ],
        user_defaults=False
        )
    logger = logging.getLogger('zc.buildout')
    logger.removeHandler(logger.handlers[0])
    logging.getLogger('zc.buildout').setLevel(99999)
    buildout.bootstrap([])
    zc.buildout.testing.install('zope.testing', eggs)
    zc.buildout.testing.install('zc.recipe.testrunner', eggs)
    zc.buildout.testing.install('zc.recipe.egg', eggs)
    zc.buildout.testing.install('zc.recipe.macro', eggs)
    return buildout


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)

    test.globs['here'] = here
    test.globs['macro'] = os.path.join('../../../..', here)
    test.globs['setupBuildout'] = (lambda *args: setupBuildout(test, *args))
    test.globs['buildout_pprint'] = buildout_pprint
    os.chdir(test.globs['macro'])
    return test

def tearDown(test):
    zc.buildout.testing.rmdir(test.globs['sample_buildout'])
    zc.buildout.testing.buildoutTearDown(test)

def test_suite():
    optionflags = (zope.testing.doctest.NORMALIZE_WHITESPACE
                   | zope.testing.doctest.ELLIPSIS
                   | zope.testing.doctest.REPORT_NDIFF)
    suite = unittest.TestSuite()
    suite.addTest(
        zope.testing.doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=tearDown,
            checker=zope.testing.renormalizing.RENormalizing([
               zc.buildout.testing.normalize_path,
               zc.buildout.testing.normalize_script,
               zc.buildout.testing.normalize_egg_py,
               zc.buildout.tests.normalize_bang,
               ]), optionflags=optionflags
            ),)

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')


