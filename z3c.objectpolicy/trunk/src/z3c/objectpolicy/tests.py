##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors
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
import unittest
from zope import component
from zope.app.testing import placelesssetup
from zope.configuration import xmlconfig
from zope.testing import module
from zope.securitypolicy.tests.test_zopepolicy import setUp

from z3c.objectpolicy.objectpolicy import ObjectPrincipalPermissionManager
from z3c.objectpolicy.objectpolicy import ObjectRolePermissionManager

def setUpOP(test):
    setUp(test)

    component.provideAdapter(ObjectPrincipalPermissionManager)
    component.provideAdapter(ObjectRolePermissionManager)

def tearDown(test):
    placelesssetup.tearDown()

def test_suite():
    from zope.testing import doctest
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'lowlevel.txt',
            setUp=setUp, tearDown=tearDown,
            ),
        doctest.DocFileSuite(
            'highlevel.txt',
            setUp=setUp, tearDown=tearDown,
            ),
        doctest.DocFileSuite(
            'zopepolicy_copy.txt',
            setUp=setUpOP, tearDown=tearDown,
            ),
        doctest.DocFileSuite(
            'zopepolicy_objectpolicy.txt',
            setUp=setUpOP, tearDown=tearDown,
            ),
        ))
