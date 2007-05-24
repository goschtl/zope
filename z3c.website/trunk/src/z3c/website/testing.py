##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Resource License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: __init__.py 40 2007-02-21 09:18:28Z roger.ineichen $
"""

import os
from zope.testing import doctest

from zope.app.testing import setup
from zope.app.testing import functional
from zope.app.testing.functional import ZCMLLayer

import z3c.testing


###############################################################################
#
# Test Component
#
###############################################################################

WebSiteLayer = os.path.join('etc', 'ftesting.zcml')
WebSiteLayer = os.path.abspath(WebSiteLayer)
WebSiteLayer = ZCMLLayer(WebSiteLayer, __name__, 'Functional')


def getRootFolder():
    return functional.FunctionalTestSetup().getRootFolder()


###############################################################################
#
# Doctest setup
#
###############################################################################

def doctestSetUp(test):
    pass


def doctestTearDown(test):
    pass


def FunctionalDocFileSuite(path, **kw):
    """Including relative path setup."""
    globs = {'getRootFolder': getRootFolder}
    if 'globs' in kw:
        globs.update(kw['globs'])
        del kw['globs']

    kw['setUp'] = kw.get('setUp', doctestSetUp)
    kw['tearDown'] = kw.get('tearDown', doctestTearDown)
    if 'package' not in kw:
        kw['package'] = doctest._normalize_module(kw.get('package', None))
    kw['module_relative'] = kw.get('module_relative', True)

    suite = functional.FunctionalDocFileSuite(path,
        optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
        globs=globs, **kw)
    suite.layer = WebSiteLayer
    return suite
