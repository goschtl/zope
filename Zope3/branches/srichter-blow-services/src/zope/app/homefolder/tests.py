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

$Id: tests.py 28311 2004-11-01 19:03:56Z jim $
"""
__docformat__ = "reStructuredText"

import unittest
from zope.security.interfaces import IPrincipal
from zope.testing import doctest
from zope.app.testing import placelesssetup, setup, ztapi

from zope.app.annotation.interfaces import IAnnotatable
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager
from zope.app.securitypolicy.principalrole import AnnotationPrincipalRoleManager
from zope.app.traversing.interfaces import IPathAdapter 

from zope.app.homefolder.homefolder import HomeFolder, getHomeFolder
from zope.app.homefolder.interfaces import IHomeFolder


def homeFolderSetUp(test):
    placelesssetup.setUp()    
    setup.setUpAnnotations()
    setup.setUpTraversal()

    ztapi.provideAdapter(IAnnotatable, IPrincipalRoleManager,
                         AnnotationPrincipalRoleManager)
    ztapi.provideAdapter(IPrincipal, IHomeFolder,
                         HomeFolder)
    ztapi.provideAdapter(IPrincipal, IPathAdapter,
                         getHomeFolder,
                         name="homefolder")

    
def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                             setUp=homeFolderSetUp,
                             tearDown=placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

