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
""" Management view component for principal-role management (Zope2's
    "local roles").

$Id: PrincipalRoleView.py,v 1.2 2002/06/10 23:28:16 jim Exp $
"""

import time
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture.ContextDependent import ContextDependent
from Zope.ComponentArchitecture import getService, getAdapter

from Zope.App.Security.IPrincipalRoleManager import IPrincipalRoleManager
from Zope.App.Security.IPrincipalRoleMap import IPrincipalRoleMap

from Zope.App.Security.IPermission import IPermission
from Zope.App.Security.IRole import IRole

class PrincipalRoleView(BrowserView):

    index = ViewPageTemplateFile('pt/principal_role_association.pt')

    def getAllPrincipals(self):

        principals = getattr(self, '_principals', None)

        if principals is None:
            principals = self._principals = getService(
                self.context, 'AuthenticationService'
                ).getPrincipals()

        return principals
    
    def getAllRoles(self):

        roles = getattr(self, '_roles', None)

        if roles is None:
            roles = self._roles = getService(self.context, 'RoleService'
                ).getRoles()

        return roles

    def createGrid( self, principals=None, roles=None ):

        if not principals:
            principals = self.getAllPrincipals()

        if not roles:
            roles = self.getAllRoles()

        return PrincipalRoleGrid( principals, roles, self.context )
        
    def action(self, principals, roles, mapping, testing=None):

        for row in mapping:
            pid = row.permission_id
            roles = row.role_ids

        if not testing:
            return self.index( 
                message="Settings changed at %s" % time.ctime(time.time())
                )


class PrincipalRoleGrid:

    def __init__( self, principals, roles, context ):    

        self._principals = principals
        self._roles = roles
        self._grid = {}

        map = getAdapter( context, IPrincipalRoleMap )

        for role in roles:
            for principal in principals:
                setting = map.getSetting( role, principal )
                self._grid[ ( role, principal ) ] = setting

    def principals( self ):
        return self._principals

    def roles( self ):
        return self._roles

    def getValue( self, role, principal ):
        return self._grid[ ( role, principal ) ]

    def listAvailableValues( self ):
        return ( 'Unset', 'Assigned', 'Removed' )

