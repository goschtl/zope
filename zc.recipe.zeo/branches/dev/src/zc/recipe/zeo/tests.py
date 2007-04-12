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
from zope.testing import doctest, renormalizing

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('zc.recipe.zeo', test)
    zc.buildout.testing.install_develop('zc.recipe.egg', test)
    zc.buildout.testing.install('ZODB3', test)
    zc.buildout.testing.install('zdaemon', test)
    zc.buildout.testing.install('ZConfig', test)
    zc.buildout.testing.install('zope.testing', test)
    zc.buildout.testing.install('zope.proxy', test)
    zc.buildout.testing.install('zope.interface', test)

def test_suite():
    return unittest.TestSuite((
        #doctest.DocTestSuite(),
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            checker=renormalizing.RENormalizing([
               zc.buildout.testing.normalize_path,
               zc.buildout.testing.normalize_script,
               zc.buildout.testing.normalize_egg_py,        
               (re.compile('#!\S+python\S*'), '#!python'),
               (re.compile('/sample-buildout/eggs/'
                           '([a-zA-Z.0-9]+)-\S+-pyN.N(-\S+)?.egg'),
                r'/sample-buildout/eggs/\1-N.N-py2.4.egg'),
               (re.compile(r"\nCouldn't find index page for 'ZODB3' "
                           r"\(maybe misspelled\?\)"),
                ''),
               ])
            ),
        
        ))
