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

import re
import zc.buildout.testing

import unittest
import zope.testing
from zope.testing import doctest, renormalizing

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('zc.recipe.deployment', test)

def test_suite():
    return unittest.TestSuite((
        #doctest.DocTestSuite(),
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            checker=renormalizing.RENormalizing([
                (re.compile('\d+ \d\d\d\d-\d\d-\d\d \d\d:\d\d'), ''),
##                zc.buildout.testing.normalize_path,
        
##                zc.buildout.testing.normalize_script,
##                zc.buildout.testing.normalize_egg_py,        
##                (re.compile('#!\S+python\S*'), '#!python'),
##                (re.compile('\d[.]\d+ seconds'), '0.001 seconds'),
##                (re.compile('zope.testing-[^-]+-'), 'zope.testing-X-'),
##                (re.compile('setuptools-[^-]+-'), 'setuptools-X-'),
               ])
            ),
        
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
