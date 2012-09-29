##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
import sys
import unittest
import zc.buildout.testing


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install('Paste', test)
    zc.buildout.testing.install('PasteDeploy', test)
    zc.buildout.testing.install('PasteScript', test)
    zc.buildout.testing.install('WebOb', test)
    zc.buildout.testing.install('WebTest', test)
    zc.buildout.testing.install('ZConfig', test)
    zc.buildout.testing.install('ZODB3', test)
    zc.buildout.testing.install('mechanize', test)
    zc.buildout.testing.install('pytz', test)
    zc.buildout.testing.install('transaction', test)
    zc.buildout.testing.install('wsgi_intercept', test)
    zc.buildout.testing.install('zc.lockfile', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install('zc.recipe.filestorage', test)
    zc.buildout.testing.install('zdaemon', test)
    zc.buildout.testing.install('zope.annotation', test)
    zc.buildout.testing.install('zope.app.appsetup', test)
    zc.buildout.testing.install('zope.app.debug', test)
    zc.buildout.testing.install('zope.app.publication', test)
    zc.buildout.testing.install('zope.app.wsgi', test)
    zc.buildout.testing.install('zope.authentication', test)
    zc.buildout.testing.install('zope.broken', test)
    zc.buildout.testing.install('zope.browser', test)
    zc.buildout.testing.install('zope.cachedescriptors', test)
    zc.buildout.testing.install('zope.component', test)
    zc.buildout.testing.install('zope.configuration', test)
    zc.buildout.testing.install('zope.container', test)
    zc.buildout.testing.install('zope.contenttype', test)
    zc.buildout.testing.install('zope.copy', test)
    zc.buildout.testing.install('zope.deferredimport', test)
    zc.buildout.testing.install('zope.dottedname', test)
    zc.buildout.testing.install('zope.error', test)
    zc.buildout.testing.install('zope.event', test)
    zc.buildout.testing.install('zope.exceptions', test)
    zc.buildout.testing.install('zope.filerepresentation', test)
    zc.buildout.testing.install('zope.i18n', test)
    zc.buildout.testing.install('zope.i18nmessageid', test)
    zc.buildout.testing.install('zope.interface', test)
    zc.buildout.testing.install('zope.lifecycleevent', test)
    zc.buildout.testing.install('zope.location', test)
    zc.buildout.testing.install('zope.minmax', test)
    zc.buildout.testing.install('zope.processlifetime', test)
    zc.buildout.testing.install('zope.proxy', test)
    zc.buildout.testing.install('zope.publisher', test)
    zc.buildout.testing.install('zope.schema', test)
    zc.buildout.testing.install('zope.security', test)
    zc.buildout.testing.install('zope.session', test)
    zc.buildout.testing.install('zope.site', test)
    zc.buildout.testing.install('zope.size', test)
    zc.buildout.testing.install('zope.testbrowser', test)
    zc.buildout.testing.install('zope.testing', test)
    zc.buildout.testing.install('zope.traversing', test)
    zc.buildout.testing.install_develop('z3c.recipe.paster', test)

    if sys.version_info < (2, 7, 0):
        # 2.6 and below needs ordereddict
        zc.buildout.testing.install('ordereddict', test)

checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    # note sure if misspelled?) has \n at the end on linux?
    (re.compile("Couldn't find index page for '[a-zA-Z0-9.]+' "
     "\(maybe misspelled\?\)\n"), ''),
    # windows doesn't have \n at the end of misspelled?)
    (re.compile("Couldn't find index page for '[a-zA-Z0-9.]+' "
     "\(maybe misspelled\?\)"), ''),
    (re.compile("""['"][^\n"']+z3c.recipe.paster[^\n"']*['"],"""),
     "'/z3c.recipe.paster',"),
    (re.compile('#![^\n]+\n'), ''),
    (re.compile('-\S+-py\d[.]\d(-\S+)?.egg'), '-pyN.N.egg'),
    # distribute prints the install_dir which pollutes the test output:
    (re.compile('install_dir .*'), ''),
    # the following are for compatibility with Windows
    (re.compile('-  .*\.exe\n'), ''),
    (re.compile('-script.py'), ''),

    ])


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('paster.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        doctest.DocFileSuite('debug.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            checker=checker),
        ))
