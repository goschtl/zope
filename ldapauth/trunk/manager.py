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
"""A LDAP manager for the ldapauth plugable authentication module.

$Id$
"""

from zope.security.proxy import trustedRemoveSecurityProxy
from zope.interface import implements

from interfaces import ILDAPManager



class LDAPManagerAdapter:
    """A LDAP manager adapter."""

    implements(ILDAPManager)

    def __init__(self, source):
        self.context = source
    
    def addPrincipal(self, login_attribute, ldap_principal):
        source = trustedRemoveSecurityProxy(self.context)
        # add a principal to the 
        pass

    def editPrincipal(self, login_attribute, ldap_principal):
        source = trustedRemoveSecurityProxy(self.context)
        # replace the principal on the ldap server with the given principal
        pass

    def deletePrincipal(self, login_attribute):
        source = trustedRemoveSecurityProxy(self.context)
        # delete the principal with the given login_attribute
        pass
