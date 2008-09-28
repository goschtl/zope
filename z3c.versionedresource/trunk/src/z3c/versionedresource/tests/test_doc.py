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
"""Versioned Resources Test Setup

$Id$
"""
__docformat__ = "reStructuredText"
import os
import unittest
import zope.interface
from zope.component import globalregistry
from zope.testing import doctest
from zope.app.testing import placelesssetup
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from z3c.versionedresource import interfaces, resource

class ITestLayer(IDefaultBrowserLayer):
    pass

class ITestLayer2(IDefaultBrowserLayer):
    pass

class ResourceFactory(object):

    def __init__(self, request):
        self.request = request

    def __repr__(self):
        return '<%s>' %self.__class__.__name__

def unregister(name):
    reg = globalregistry.globalSiteManager.adapters
    reg.unregister((IDefaultBrowserLayer,), interfaces.IVersionedResource, name)

def ls(dir):
    for name in sorted(os.listdir(dir)):
        path = os.path.join(dir, name)
        print '%s %s\t%i' %(
            'd' if os.path.isdir(path) else 'f',
            name,
            os.stat(path).st_size)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            '../README.txt',
            setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown,
            globs = {'ls': ls, 'unregister': unregister},
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
        ))
