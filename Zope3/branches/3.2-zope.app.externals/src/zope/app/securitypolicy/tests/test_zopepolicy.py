##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Tests the zope policy.

$Id$
"""

import unittest
from zope.testing.doctestunit import DocFileSuite
from zope.app import zapi
from zope.app.testing import placelesssetup, ztapi
from zope.app.annotation.interfaces import IAnnotatable
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.annotation.interfaces import IAnnotations
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.securitypolicy.interfaces import IGrantInfo
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager
from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.app.securitypolicy.interfaces import IRolePermissionManager
from zope.app.securitypolicy.principalpermission \
     import AnnotationPrincipalPermissionManager
from zope.app.securitypolicy.principalrole \
     import AnnotationPrincipalRoleManager
from zope.app.securitypolicy.rolepermission \
     import AnnotationRolePermissionManager
from zope.app.securitypolicy.grantinfo \
     import AnnotationGrantInfo
from zope.security.management import endInteraction

def setUp(test):
    placelesssetup.setUp()
    endInteraction()
    ztapi.provideAdapter(
        IAttributeAnnotatable, IAnnotations,
        AttributeAnnotations)
    ztapi.provideAdapter(
        IAnnotatable, IPrincipalPermissionManager,
        AnnotationPrincipalPermissionManager)
    ztapi.provideAdapter(
        IAnnotatable, IPrincipalRoleManager,
        AnnotationPrincipalRoleManager)
    ztapi.provideAdapter(
        IAnnotatable, IRolePermissionManager,
        AnnotationRolePermissionManager)
    ztapi.provideAdapter(
        IAnnotatable, IGrantInfo,
        AnnotationGrantInfo)


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('zopepolicy.txt',
                     package='zope.app.securitypolicy',
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
