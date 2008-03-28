##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""test setup

$Id$
"""
__docformat__ = "reStructuredText"

import doctest, unittest
from zope import component
from zope.app.testing import placelesssetup
from zope.traversing import testing
from zope.traversing.interfaces import ITraversable
from zope.traversing.namespace import view
from zope.app.publisher.browser.fileresource import FileResource

from z3ext.resource import fileresource
from z3ext.resource.interfaces import IResourceFactoryType


class CustomResource(fileresource.FileResource):
    pass
    

class CustomFileResourceFactory(fileresource.FileResourceFactory):

    def __call__(self, request):
        resource = CustomResource(self._file, request)
        resource.__Security_checker__ = self._checker
        resource.__name__ = self._name
        return resource


def setUp(test):
    placelesssetup.setUp(test)
    testing.setUp()
    component.provideAdapter(view, (None, None), ITraversable, name="view")

    component.provideUtility(
        fileresource.filefactory, IResourceFactoryType)
    component.provideUtility(
        fileresource.filefactory, IResourceFactoryType, name='fileresource')
    component.provideUtility(
        fileresource.imagefactory, IResourceFactoryType, name='imageresource')

    component.provideAdapter(
        fileresource.FileResourceAdapter, (FileResource,))


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp, tearDown=placelesssetup.tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
         ))
