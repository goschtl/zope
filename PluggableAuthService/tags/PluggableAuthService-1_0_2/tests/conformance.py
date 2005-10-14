##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights
# Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this
# distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
""" Base classes for testing plugin interface conformance.

$Id$
"""

class IExtractionPlugin_conformance:

    def test_IExtractionPlugin_conformance( self ):

        from Interface.Verify import verifyClass
        from Products.PluggableAuthService.interfaces.plugins \
            import IExtractionPlugin

        verifyClass( IExtractionPlugin, self._getTargetClass() )

class ILoginPasswordExtractionPlugin_conformance:

    def test_ILoginPasswordExtractionPlugin_conformance( self ):

        from Interface.Verify import verifyClass
        from Products.PluggableAuthService.interfaces.plugins \
            import ILoginPasswordExtractionPlugin

        verifyClass( ILoginPasswordExtractionPlugin, self._getTargetClass() )

class ILoginPasswordHostExtractionPlugin_conformance:

    def test_ILoginPasswordHostExtractionPlugin_conformance( self ):

        from Interface.Verify import verifyClass
        from Products.PluggableAuthService.interfaces.plugins \
            import ILoginPasswordHostExtractionPlugin

        verifyClass( ILoginPasswordHostExtractionPlugin
                   , self._getTargetClass() )

class IChallengePlugin_conformance:

    def test_IChallengePlugin_conformance( self ):

        from Interface.Verify import verifyClass
        from Products.PluggableAuthService.interfaces.plugins \
            import IChallengePlugin

        verifyClass( IChallengePlugin, self._getTargetClass() )

class ICredentialsUpdatePlugin_conformance:

    def test_ICredentialsUpdatePlugin_conformance( self ):

        from Interface.Verify import verifyClass
        from Products.PluggableAuthService.interfaces.plugins \
            import ICredentialsUpdatePlugin

        verifyClass( ICredentialsUpdatePlugin, self._getTargetClass() )

class ICredentialsResetPlugin_conformance:

    def test_ICredentialsResetPlugin_conformance( self ):

        from Interface.Verify import verifyClass
        from Products.PluggableAuthService.interfaces.plugins \
            import ICredentialsResetPlugin

        verifyClass( ICredentialsResetPlugin, self._getTargetClass() )


class IAuthenticationPlugin_conformance:

    def test_AuthenticationPlugin_conformance( self ):

        from Interface.Verify import verifyClass
        from Products.PluggableAuthService.interfaces.plugins \
            import IAuthenticationPlugin

        verifyClass( IAuthenticationPlugin, self._getTargetClass() )


class IUserEnumerationPlugin_conformance:

    def test_UserEnumerationPlugin_conformance( self ):

        from Interface.Verify import verifyClass
        from Products.PluggableAuthService.interfaces.plugins \
            import IUserEnumerationPlugin

        verifyClass( IUserEnumerationPlugin, self._getTargetClass() )


class IUserAdderPlugin_conformance:

    def test_UserAdderPlugin_conformance( self ):

        from Interface.Verify import verifyClass
        from Products.PluggableAuthService.interfaces.plugins \
            import IUserAdderPlugin

        verifyClass( IUserAdderPlugin, self._getTargetClass() )


class IGroupEnumerationPlugin_conformance:

    def test_GroupEnumerationPlugin_conformance( self ):

        from Interface.Verify import verifyClass
        from Products.PluggableAuthService.interfaces.plugins \
            import IGroupEnumerationPlugin

        verifyClass( IGroupEnumerationPlugin, self._getTargetClass() )


class IGroupsPlugin_conformance:

    def test_GroupsPlugin_conformance( self ):

        from Interface.Verify import verifyClass
        from Products.PluggableAuthService.interfaces.plugins \
            import IGroupsPlugin

        verifyClass( IGroupsPlugin, self._getTargetClass() )


class IRoleEnumerationPlugin_conformance:

    def test_RoleEnumerationPlugin_conformance( self ):

        from Interface.Verify import verifyClass
        from Products.PluggableAuthService.interfaces.plugins \
            import IRoleEnumerationPlugin

        verifyClass( IRoleEnumerationPlugin, self._getTargetClass() )


class IRolesPlugin_conformance:

    def test_RolesPlugin_conformance( self ):

        from Interface.Verify import verifyClass
        from Products.PluggableAuthService.interfaces.plugins \
            import IRolesPlugin

        verifyClass( IRolesPlugin, self._getTargetClass() )

class IRoleAssignerPlugin_conformance:

    def test_RoleAssignerPlugin_conformance( self ):

        from Interface.Verify import verifyClass
        from Products.PluggableAuthService.interfaces.plugins \
            import IRoleAssignerPlugin

        verifyClass( IRoleAssignerPlugin, self._getTargetClass() )
