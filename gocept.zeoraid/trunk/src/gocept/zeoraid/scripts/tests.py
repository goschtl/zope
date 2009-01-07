##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
    zc.buildout.testing.install_develop('gocept.zeoraid', test)
    zc.buildout.testing.install('zc.lockfile', test)
    zc.buildout.testing.install('zc.zodbrecipes', test)
    zc.buildout.testing.install('zope.event', test)
    zc.buildout.testing.install('zope.testing', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install('zdaemon', test)
    zc.buildout.testing.install('ZConfig', test)
    zc.buildout.testing.install('ZODB3', test)
    zc.buildout.testing.install('transaction', test)
    zc.buildout.testing.install('zope.proxy', test)
    zc.buildout.testing.install('zope.interface', test)


checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    (re.compile(
    "Couldn't find index page for '[a-zA-Z0-9.]+' "
    "\(maybe misspelled\?\)"
    "\n"
    ), ''),
    (re.compile('#![^\n]+\n'), ''),                
    (re.compile('-\S+-py\d[.]\d(-\S+)?.egg'),
     '-pyN.N.egg',
    ),
    ])

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'recipe.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            checker=checker,
            optionflags=doctest.REPORT_NDIFF|doctest.ELLIPSIS
            ),
        ))
