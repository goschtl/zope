##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for SecurityManagement

$Id: test_securitymanagement.py,v 1.2 2002/12/25 14:15:22 jim Exp $
"""

import unittest

from zope.interface.verify import verifyObject
from zope.testing.cleanup import CleanUp

import zope.security.securitymanagement
from zope.security.securitymanagement import \
     noSecurityManager, setSecurityPolicy, newSecurityManager


class Test(CleanUp, unittest.TestCase):

    def test_import( self ):
        from zope.security import securitymanagement
        from zope.security.interfaces import ISecurityManagement
        from zope.security.interfaces \
            import ISecurityManagementSetup

        verifyObject( ISecurityManagementSetup, securitymanagement )
        verifyObject( ISecurityManagement, securitymanagement )

    def test_ISecurityManagementSetup( self ):

        from zope.security.securitymanagement import noSecurityManager
        from zope.security.securitymanagement import newSecurityManager
        from zope.security.securitymanagement import replaceSecurityManager

        some_user = []
        other_user = []
        old = newSecurityManager( some_user )
        self.assertEqual( old, None )

        old = newSecurityManager( other_user )
        self.failUnless( old is not None )
        self.failUnless( old.getPrincipal() is some_user )

        old2 = replaceSecurityManager( old )
        self.failUnless( old2 is not None )
        self.failUnless( old2.getPrincipal() is other_user )

        noSecurityManager()

    def test_getSecurityManager( self ):
        # This is a test for the case when there is no principal

        from zope.security.securitymanagement import noSecurityManager
        from zope.security.securitymanagement import replaceSecurityManager
        from zope.security.securitymanagement import getSecurityManager

        noSecurityManager()
        self.failUnless( replaceSecurityManager( None ) is None )

        mgr = getSecurityManager()
        self.assertEqual( mgr.getPrincipal(), None)
        # XXX maybe add test for default principal case
        self.failIf( mgr.calledByExecutable() )
        self.assertEqual( replaceSecurityManager( None ), mgr )

        noSecurityManager()

    def _setPermissive( self ):
        from zope.security.securitymanagement import setSecurityPolicy
        from zope.security.simplesecuritypolicies \
                                import PermissiveSecurityPolicy
        setSecurityPolicy( PermissiveSecurityPolicy() )

    def _setParanoid( self ):
        from zope.security.securitymanagement import setSecurityPolicy
        from zope.security.simplesecuritypolicies \
                                import ParanoidSecurityPolicy
        setSecurityPolicy( ParanoidSecurityPolicy() )

    def test_setSecurityPolicy( self ):

        from zope.security.securitymanagement import noSecurityManager
        from zope.security.securitymanagement import getSecurityManager
        from zope.exceptions import Unauthorized

        # test against default policy (paranoid)
        self._setParanoid()
        newSecurityManager('some user')
        mgr = getSecurityManager()
        self.failIf( mgr.checkPermission( None, None ) )

        # test against explicit permissive policy
        self._setPermissive()
        newSecurityManager('some user')
        mgr = getSecurityManager()
        self.failUnless( mgr.checkPermission( None, None ) )

        # test against explicit paranoid policy
        self._setParanoid()
        newSecurityManager('some user')
        mgr = getSecurityManager()
        self.failIf( mgr.checkPermission( None, None ) )


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
