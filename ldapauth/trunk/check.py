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
            conn = getattr(source, '_v_conn', None)
            if conn:
                self.report.append('... connection "%s" found' % conn)
            else:
                self.report.append("... no existing connection found")
                self.report.append("... try to connect")
             
            if not conn:
                connectstring = 'ldap://%s:%s' % (source.host, source.port)
                self.report.append("... ... connecting to:")
                self.report.append("... ... %s" % connectstring)
                connection = ldap.initialize(connectstring)
                self.report.append("... <strong>Connection OK!</strong>")
                return self.report
            else:
                self.report.append("... <strong>Connection OK!</strong>")
                return self.report
        except:
            self.report.append("... <strong>Connection test faild!</strong>")
            return self.report
            
 
