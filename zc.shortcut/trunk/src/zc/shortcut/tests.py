##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""tests for shortcut package

$Id$
"""
import unittest

import zope.testing.module

from zope.testing import doctest
from zope.app.testing import placelesssetup

def adaptersSetUp(test):
    zope.testing.module.setUp(test, name='zc.shortcut.adapters_test')
    placelesssetup.setUp(test)

def adaptersTearDown(test):
    zope.testing.module.tearDown(test, name='zc.shortcut.adapters_test')
    placelesssetup.tearDown(test)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'adapters.txt',
            setUp=adaptersSetUp, tearDown=adaptersTearDown,
            optionflags=doctest.ELLIPSIS),
        doctest.DocFileSuite(
            'shortcut.txt', 'proxy.txt', 'adding.txt', 'factory.txt',
            setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown,
            optionflags=doctest.ELLIPSIS),
        doctest.DocTestSuite('zc.shortcut.constraints'),
        ))
