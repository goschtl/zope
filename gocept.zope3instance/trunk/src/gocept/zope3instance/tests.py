##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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

import os, re, shutil, sys, tempfile
import pkg_resources

import zc.buildout.testing

import unittest
import zope.testing
from zope.testing import doctest, renormalizing


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('gocept.zope3instance', test)
    zc.buildout.testing.install('zope.testing', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    sample_zope3 = test.globs['tmpdir']('sample_zope3')
    test.globs['sample_zope3'] = sample_zope3
    test.globs['mkdir'](sample_zope3, 'src')
    test.globs['mkdir'](sample_zope3, 'zopeskel')
    test.globs['mkdir'](sample_zope3, 'zopeskel', 'etc')

    test.globs['write'](sample_zope3, 'zopeskel', 'etc', 
                        'ftesting.zcml', 'This is ftesting')
    test.globs['write'](sample_zope3, 'zopeskel', 'etc', 
                        'site.zcml', 'This is site')
    test.globs['mkdir'](sample_zope3, 'zopeskel', 'package-includes')


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            checker=renormalizing.RENormalizing([
               ])
            ),
        ))
