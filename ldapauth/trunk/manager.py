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
"""A LDAP manager for the ldapauth plugable authentication module.

$Id$
"""

from zope.interface import implements
from zope.security.proxy import trustedRemoveSecurityProxy

from interfaces import ILDAPManager


class LDAPManagerAdapter:
    """A LDAP manager adapter."""

    implements(ILDAPManager)

    def __init__(self, source):
        self.context = source
    
    def addPrincipal(self, ldap_principal):
        # register the principal with the principal source
        source = trustedRemoveSecurityProxy(self.context)
        source[ldap_principal.login] = ldap_principal
        
    def editPrincipal(self, ldap_principal):
        # register the principal with the principal source
        source = trustedRemoveSecurityProxy(self.context)
        source[ldap_principal.login] = ldap_principal

    def deletePrincipal(self, login):
        # unregister the principal with the principal source
        source = trustedRemoveSecurityProxy(self.context)
        del source[login]
