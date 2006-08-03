##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for UserAllowedPolicies

$Id$
"""
import unittest

from Products.PluggableAuthService.tests.conformance \
    import IUserAllowedPolicyPlugin_conformance

class PolicyTestBase( unittest.TestCase
                    , IUserAllowedPolicyPlugin_conformance
                    ):

    # must supply '_getTargetClass'

    def _makeOne( self, *args, **kw ):
        return self._getTargetClass()( *args, **kw )

class ShortcutAllowPolicyTests( PolicyTestBase ):

    def _getTargetClass( self ):
        from Products.PluggableAuthService.plugins.UserAllowedPolicies \
            import ShortcutAllowPolicy
        return ShortcutAllowPolicy
    
    def test_pass_wo_anonymous_or_authenticated_in_roles( self ):
        plugin = self._makeOne()
        user = DummyUser()
        obj = object()
        obj_roles = ( 'Role A', )
        allowed = plugin.isUserAllowed( user, obj, obj_roles )
        self.assertEqual(allowed, None)
    
    def test_allows_for_public( self ):
        plugin = self._makeOne()
        user = DummyUser()
        obj = object()
        obj_roles = None # classic Zope "public"
        allowed = plugin.isUserAllowed( user, obj, obj_roles )
        self.failUnless(allowed)
    
    def test_allows_for_Anonymous_in_roles( self ):
        plugin = self._makeOne()
        user = DummyUser()
        obj = object()
        obj_roles = ( 'Anonymous', )
        allowed = plugin.isUserAllowed( user, obj, obj_roles )
        self.failUnless(allowed)
    
    def test_allows_for_Authenticated_in_roles_not_anonymous( self ):
        plugin = self._makeOne()
        user = DummyUser()
        obj = object()
        obj_roles = ( 'Authenticated', )
        allowed = plugin.isUserAllowed( user, obj, obj_roles )
        self.failUnless(allowed)
    
    def test_pass_for_Authenticated_in_roles_and_anonymous( self ):
        plugin = self._makeOne()
        user = DummyUser( 'Anonymous User' )
        obj = object()
        obj_roles = ( 'Authenticated', )
        allowed = plugin.isUserAllowed( user, obj, obj_roles )
        self.assertEqual(allowed, None)

class GlobalRolesAllowPolicyTests( PolicyTestBase ):

    def _getTargetClass( self ):
        from Products.PluggableAuthService.plugins.UserAllowedPolicies \
            import GlobalRolesAllowPolicy
        return GlobalRolesAllowPolicy
    
    def test_pass_for_no_match_in_roles( self ):
        plugin = self._makeOne()
        user = DummyUser()
        obj = object()
        obj_roles = ( 'Role A', )
        allowed = plugin.isUserAllowed( user, obj, obj_roles )
        self.assertEqual(allowed, None)
    
    def test_allow_for_match_in_roles_and_in_context( self ):
        plugin = self._makeOne()
        user = DummyUser( roles=( 'Role B', ), in_context=True )
        obj = object()
        obj_roles = ( 'Role A', 'Role B', 'Role C' )
        allowed = plugin.isUserAllowed( user, obj, obj_roles )
        self.failUnless(allowed)
    
    def test_disallow_for_match_in_roles( self ):
        plugin = self._makeOne()
        user = DummyUser( roles=( 'Role B', ), in_context=False )
        obj = object()
        obj_roles = ( 'Role A', 'Role B', 'Role C' )
        allowed = plugin.isUserAllowed( user, obj, obj_roles )
        self.failIf(allowed)

class DummyUser:
    def __init__( self, name='Dummy User', roles=(), in_context=True
                , shared_roles=None ):
        self.name = name
        self.roles = roles
        self.in_context = in_context
        self.shared_roles = shared_roles

    def getUserName( self ):
        return self.name

    def getRoles( self ):
        return self.roles

    def _check_context( self, object ):
        return self.in_context

    def _shared_roles( self, object ):
        return self.shared_roles

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite( ShortcutAllowPolicyTests ),
        unittest.makeSuite( GlobalRolesAllowPolicyTests ),
        ))

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
