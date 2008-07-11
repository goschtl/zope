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

import os
import re
import zc.buildout.testing
import zc.buildout.tests

import unittest
import zc.recipe.egg
import zc.recipe.macro
import zc.recipe.testrunner
import zope.testing
import zope.testing.doctest
import zope.testing.renormalizing

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)

    zc.buildout.testing.install('zope.testing', test)
    zc.buildout.testing.install('zc.recipe.testrunner', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install('zc.recipe.macro', test)
    return test

def test_suite():
    optionflags = (zope.testing.doctest.NORMALIZE_WHITESPACE
                   | zope.testing.doctest.ELLIPSIS
                   | zope.testing.doctest.REPORT_NDIFF)
    suite = unittest.TestSuite()
    suite.addTest(
        zope.testing.doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
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


