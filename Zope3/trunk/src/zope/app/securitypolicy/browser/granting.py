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
"""Granting Roles and Permissions to Principals

$Id$
"""
__docformat__ = "reStructuredText"
import zope.schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.app import zapi
from zope.app.security.vocabulary import PrincipalSource
from zope.app.form.utility import setUpWidget
from zope.app.i18n import ZopeMessageIDFactory as _

from zope.app.form.interfaces import IInputWidget
from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager
from zope.app.securitypolicy.interfaces import IRole
from zope.app.security.interfaces import IPermission
from zope.app.security import settings

settings_vocabulary = SimpleVocabulary(
    [SimpleTerm(settings.Allow, token="allow", title=_('Allow')),
     SimpleTerm(settings.Unset, token="unset", title=_('Unset')),
     SimpleTerm(settings.Deny,  token='deny',  title=_('Deny')),
     ])

class Granting(object):

    principal = None

    principal_field = zope.schema.Choice(
        __name__ = 'principal',
        source=PrincipalSource(),
        required=True)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def status(self):
        setUpWidget(self, 'principal', self.principal_field, IInputWidget)
        if not self.principal_widget.hasInput():
            return u''
        
        principal = self.principal_widget.getInputValue()
        self.principal = principal

        roles = [role for name, role in zapi.getUtilitiesFor(IRole)]
        roles.sort(lambda x, y: cmp(x.title, y.title))
        principal_roles = IPrincipalRoleManager(self.context)

        self.roles = []
        for role in roles:
            name = principal + '.role.'+role.id
            field = zope.schema.Choice(__name__= name,
                                       title=role.title,
                                       vocabulary=settings_vocabulary)
            setUpWidget(self, name, field, IInputWidget,
                        principal_roles.getSetting(role.id, principal))
            self.roles.append(getattr(self, name+'_widget'))

        perms = [perm for name, perm in zapi.getUtilitiesFor(IPermission)]
        perms.sort(lambda x, y: cmp(x.title, y.title))
        principal_perms = IPrincipalPermissionManager(self.context)

        self.permissions = []
        for perm in perms:
            if perm.id == 'zope.Public':
                continue
            name = principal + '.permission.'+perm.id
            field = zope.schema.Choice(__name__=name,
                                       title=perm.title,
                                       vocabulary=settings_vocabulary)
            setUpWidget(self, name, field, IInputWidget,
                        principal_perms.getSetting(perm.id, principal))
            self.permissions.append(
                getattr(self, name+'_widget'))

        if 'GRANT_SUBMIT' not in self.request:
            return u''
        
        for role in roles:
            name = principal + '.role.'+role.id
            role_widget = getattr(self, name+'_widget')
            if role_widget.hasInput():
                setting = role_widget.getInputValue()
                # Arrgh!
                if setting is settings.Allow:
                    principal_roles.assignRoleToPrincipal(
                        role.id, principal)
                elif setting is settings.Deny:
                    principal_roles.removeRoleFromPrincipal(
                        role.id, principal)
                else:
                    principal_roles.unsetRoleForPrincipal(
                        role.id, principal)
        
        for perm in perms:
            if perm.id == 'zope.Public':
                continue
            name = principal + '.permission.'+perm.id
            perm_widget = getattr(self, name+'_widget')
            if perm_widget.hasInput():
                setting = perm_widget.getInputValue()
                # Arrgh!
                if setting is settings.Allow:
                    principal_perms.grantPermissionToPrincipal(
                        perm.id, principal)
                elif setting is settings.Deny:
                    principal_perms.denyPermissionToPrincipal(
                        perm.id, principal)
                else:
                    principal_perms.unsetPermissionForPrincipal(
                        perm.id, principal)
                    
        return u'Grants updated.'
