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
"""A plugable authentication module for LDAP.

$Id$
"""
import ldap
from zope.security.proxy import trustedRemoveSecurityProxy
from zope.interface import implements
from zope.app.pluggableauth import SimplePrincipal

from interfaces import ICheckLDAPAdapter

class CheckLDAPAdapter:
    """A LDAP connection test adapter."""

    implements(ICheckLDAPAdapter)

    def __init__(self, context):
        self.context = context
        self.report = []
    
    def testConnection(self):
        self.report = []
        source = trustedRemoveSecurityProxy(self.context)
        self.report.append("... check existing connection")

        try:
            connection = getattr(source, "_v_conn", None)

            if connection != None:
                self.report.append("... connection found")
                self.report.append("... bind connection to LDAP server")
                connection.simple_bind_s(source.manager_dn,
                        source.manager_passwd)
                self.report.append("... <strong>OK!</strong>")
                return self.report
            else:
                self.report.append("... no existing connection found")
                connectstring = "ldap://%s:%s" % (source.host, source.port)
                self.report.append("... setup connection to: %s" % connectstring)
                connection = ldap.initialize(connectstring)
                
                try:
                    self.report.append("... bind connection to LDAP server")
                    connection.simple_bind_s(source.manager_dn,
                            source.manager_passwd)
                    self.report.append("... <strong>OK!</strong>")
                    return self.report
                except:
                    self.report.append("... No LDAP server found")
                    self.report.append("... <strong>Test faild!</strong>")
                    return self.report

        except:
            self.report.append("... <strong>Test faild!</strong>")
            return self.report
            
    def testGetPrincipals(self, name):
        self.report = []
        source = trustedRemoveSecurityProxy(self.context)

        try:
            connectstring = "ldap://%s:%s" % (source.host, source.port)
            self.report.append("... setup connection to: %s" % connectstring)
            l = self._connect(source)
            self.report.append("... bind connection to LDAP server")
            l.simple_bind_s(source.manager_dn, source.manager_passwd)
            
            if name == "" :
                self.report.append("... test without a  name")
                search = "(%s=*)" % source.login_attribute
                self.report.append("... search string '%s'" % search)
            else:
                self.report.append("... test with name '%s'" % name)
                search = "(%s=*%s*)" % (source.login_attribute, name)
                self.report.append("... search string '%s'" % search)
            
            self.report.append("... search on LDAP server")
            lsearch = l.search_s(source.basedn, ldap.SCOPE_ONELEVEL, search)
            if lsearch:
                self.report.append("... ... found %s items" % len(lsearch))
            
            self.report.append("... convert LDAP entries to principals")
            principals = []
            for node in lsearch:
                node_dn, node_dict = node
                principal = SimplePrincipal(
                        login = node_dict[source.login_attribute][0],
                        password = node_dict['userPassword'][0])
                principals.append(principal)

            if len(principals):
                self.report.append("... ... converted %s LDAP item(s) to principals" % len(principals))
                self.report.append("... <strong>OK!</strong>")
                return self.report
            else:
                self.report.append("... ... there no entries found on the LDAP server")
                self.report.append("... ... perhpas you tried a wrong search query")
                self.report.append("... ... or you don't have data on the LDAP server")
                self.report.append("... <strong>Maybe OK!</strong>")
                return self.report
                

        except:
            self.report.append("... <strong>Test faild!</strong>")
            return self.report


    # helper methods
    def _connect(self, source):
        connectstring = "ldap://%s:%s" % (source.host, source.port)
        connection = ldap.initialize(connectstring)
        return connection
