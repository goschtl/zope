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

from zope.testing import renormalizing
import doctest
import re
import unittest
import zc.buildout.testing


def test_start_error():
    """The start script will setup a egg based start hook for a Zope 3 setup.
    Let's create a buildout that installs it as an ordinary script:

    >>> write('buildout.cfg',
    ... '''
    ... [app]
    ... recipe = z3c.recipe.dev:app
    ... eggs = z3c.recipe.dev
    ... servers = zserver
    ... ''')

    >>> print system(join('bin', 'buildout')),

    """


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('z3c.recipe.dev', test)
    zc.buildout.testing.install('zope.testing', test)
    zc.buildout.testing.install('zope.interface', test)
    zc.buildout.testing.install('zope.exceptions', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install('ZConfig', test)
    zc.buildout.testing.install('zc.recipe.filestorage', test)


checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    (re.compile(
    "Couldn't find index page for '[a-zA-Z0-9.]+' "
    "\(maybe misspelled\?\)"
    "\n"
    ), ''),
    (re.compile("""['"][^\n"']+z3c.recipe.dev[^\n"']*['"],"""),
     "'/z3c.recipe.dev',"),
    (re.compile("""['"][^\n"']+site-packages[^\n"']*['"],"""),
     "'/site-packages',"),
    (re.compile('#![^\n]+\n'), ''),
    (re.compile('-\S+-py\d[.]\d(-\S+)?.egg'),
     '-pyN.N.egg',
    ),
    (re.compile('install_dir .*'), ''),
    zc.buildout.testing.normalize_path,
    zc.buildout.testing.normalize_script,
    zc.buildout.testing.normalize_egg_py,
    ])


def test_suite():
    return unittest.TestSuite(
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE,
            checker=checker),
        )
