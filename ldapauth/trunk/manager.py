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

import ldap

from zope.interface import implements
from zope.security.proxy import trustedRemoveSecurityProxy

from interfaces import ILDAPManager


# This is a really crude hack. I really think we should use a way to
# represent ldap connection as some sort of a database, using more
# sophisticated methods than the ones here.
#
# I'm working on it.

class LDAPManagerAdapter:
    """A LDAP manager adapter."""

    implements(ILDAPManager)

    def __init__(self, source):
        self.context = source
    
    # Lack the verification of the schema.
    def addPrincipal(self, ldap_principal):
        source = trustedRemoveSecurityProxy(self.context)
        l = self.__connect(source)
        dn = self._createdn(ldap_principal, source)
        modification = ldap.modlist.addModlist(
                {source.login_attribute : ldap_principal.login,
                 'userPassword' : ldap_principal.password})
        l.add_s(dn, modification)
        # register the principal with the principal source
        source[ldap_principal.login] = ldap_principal
        
    def editPrincipal(self, ldap_principal):
        source = trustedRemoveSecurityProxy(self.context)

    def deletePrincipal(self, login):
        source = trustedRemoveSecurityProxy(self.context)

    def _createdn(self, principal, ldapauth):
        return '%s=%s,%s' % (ldapauth.login_attribute,
                principal.login,
                ldapauth.basedn)

    def __connect(self, source):
        conn = getattr(self, '_v_conn', None)
        if conn is None:
            connectstring = 'ldap://%s:%s' % (source.host, source.port)
            connection = ldap.initialize(connectstring)
            self._v_conn = connection
            return connection
        else:
            return conn
