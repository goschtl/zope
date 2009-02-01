##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Homefolder Tests

$Id$
"""
__docformat__ = "reStructuredText"

import unittest
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import classImplements
from zope.security.interfaces import IPrincipal
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.securitypolicy.principalrole import AnnotationPrincipalRoleManager
from zope.traversing.interfaces import IPathAdapter
from zope.testing import doctest

from zope.app.testing import placelesssetup, setup, ztapi
from zope.app.file import File

from zope.app.homefolder.homefolder import HomeFolder, getHomeFolder
from zope.app.homefolder.interfaces import IHomeFolder

from zope.app.folder.folder import Folder
from zope.app.folder.interfaces import IFolder
from zope.security.checker import InterfaceChecker, defineChecker

def homeFolderSetUp(test):
    placelesssetup.setUp()
    setup.setUpAnnotations()
    setup.setUpTraversal()

    classImplements(File, IAttributeAnnotatable)

    ztapi.provideAdapter(IAnnotatable, IPrincipalRoleManager,
                         AnnotationPrincipalRoleManager)
    ztapi.provideAdapter(IPrincipal, IHomeFolder,
                         HomeFolder)
    ztapi.provideAdapter(IPrincipal, IPathAdapter,
                         getHomeFolder,
                         name="homefolder")

    testChecker = InterfaceChecker(IFolder)
    defineChecker(Folder, testChecker)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                             setUp=homeFolderSetUp,
                             tearDown=placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

