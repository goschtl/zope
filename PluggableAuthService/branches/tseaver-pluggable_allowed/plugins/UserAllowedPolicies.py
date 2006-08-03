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
""" Policies for plugging into 'PropertiedUser.allowed()'

$Id$
"""
from AccessControl.SecurityInfo import ClassSecurityInfo
from App.class_init import default__class_init__ as InitializeClass

from Products.PluggableAuthService.interfaces.plugins \
    import IUserAllowedPolicyPlugin
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements

class ShortcutAllowPolicy( BasePlugin ):

    """ Plugin for traditional "shortcut" allow policy.
    """
    meta_type = 'Shortcut Allow Policy'

    security = ClassSecurityInfo()

    security.declarePrivate( 'isUserAllowed' )
    def isUserAllowed( self, user, object, object_roles ):
        """ See IUserAllowedPolicyPlugin.
        """
        # Short-circuit the common case of anonymous access.
        if object_roles is None or 'Anonymous' in object_roles:
            return True

        # Provide short-cut access if object is protected by 'Authenticated'
        # role and user is not nobody
        if 'Authenticated' in object_roles and (
            user.getUserName() != 'Anonymous User'):
            return True

        return None # pass

classImplements( ShortcutAllowPolicy
               , IUserAllowedPolicyPlugin
               )

InitializeClass( ShortcutAllowPolicy )

class GlobalRolesAllowPolicy( BasePlugin ):

    """ Plugin for traditional allow policy using global roles.
    """
    meta_type = 'Global Roles Allow Policy'

    security = ClassSecurityInfo()

    security.declarePrivate( 'isUserAllowed' )
    def isUserAllowed( self, user, object, object_roles ):
        """ See IUserAllowedPolicyPlugin.
        """
        user_roles = user.getRoles()

        for role in object_roles:
            if role in user_roles:
                return user._check_context(object)

        return None # pass

classImplements( GlobalRolesAllowPolicy
               , IUserAllowedPolicyPlugin
               )

InitializeClass( GlobalRolesAllowPolicy )
