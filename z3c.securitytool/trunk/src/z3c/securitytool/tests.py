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

$Id: test_zopepolicy.py 73662 2007-03-27 06:52:40Z dobe $
"""

import unittest, doctest
from zope.testing import module
from zope.testing.doctestunit import DocFileSuite

from zope.interface import Interface
from zope.component import provideAdapter
from zope.annotation.interfaces import IAnnotatable
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.annotation.interfaces import IAnnotations
from zope.annotation.attribute import AttributeAnnotations
from zope.security.management import endInteraction

from zope.app.testing import placelesssetup, ztapi
from zope.securitypolicy.interfaces import IGrantInfo
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.securitypolicy.interfaces import IRolePermissionManager
from zope.securitypolicy.principalpermission \
     import AnnotationPrincipalPermissionManager
from zope.securitypolicy.principalrole \
     import AnnotationPrincipalRoleManager
from zope.securitypolicy.rolepermission \
     import AnnotationRolePermissionManager
from zope.securitypolicy.grantinfo \
     import AnnotationGrantInfo
from zope.app.authentication import principalfolder

from z3c.securitytool.securitytool import SecurityChecker

def setUp(test):
    placelesssetup.setUp()
#    endInteraction()
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
    # createPrincipalFolder(test)
    # createPrincipals(test,'randy')
    # createPrincipals(test,'markus')
    # createPrincipals(test,'daniel')

    module.setUp(test, 'z3c.securitytool.securitytool.README')
    provideAdapter(SecurityChecker, (Interface,))

# def defineRole(id, title=None, description=None):
#     role = Role(id, title, description)
#     ztapi.provideUtility(IRole, role, name=role.id)
#     return role
# 
# def definePermission(id, title=None, description=None):
#     perm = Permission(id, title, description)
#     ztapi.provideUtility(IPermission, perm, name=perm.id)
#     return perm
# 
# def createPrincipalFolder(test):
#     test.globs['pf'] = principalfolder.PrincipalFolder(u'Members.')
#     
# def createPrincipals(test,name):
#     principal = principalfolder.InternalPrincipal(
#             name,'password',name,'SHA1')
#     test.globs['pf'][name] = principal
    
    
def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    
    return unittest.TestSuite((
        DocFileSuite('README.txt',optionflags=flags,
                     setUp=setUp, tearDown=placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
